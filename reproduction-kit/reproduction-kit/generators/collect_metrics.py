#!/usr/bin/env python3
"""Codex rollout 로그에서 턴 단위 토큰·시간·비용 지표를 추출한다.

사용법:
  python3 collect_metrics.py                          # 오늘 세션 전체
  python3 collect_metrics.py --since 2026-07-11T19:00 # 특정 시각 이후
  python3 collect_metrics.py --cwd-filter gpt56-scaling  # 테스트 폴더 세션만
  python3 collect_metrics.py -o runs.csv              # CSV 저장

원리: ~/.codex/sessions/YYYY/MM/DD/rollout-*.jsonl 을 파싱.
  - turn_context  → model / effort / cwd (조합 라벨)
  - user_message / task_started → 턴 시작 시각
  - token_count(last_token_usage) → 턴별 input/cached/output/reasoning 토큰
  - task_complete → 턴 종료 시각
  - rate_limits.used_percent → 구독 소진 (5h/주간 창)
훅 불필요 — 이미 돌린 세션도 소급 분석 가능.
"""
import argparse
import csv
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

SESSIONS_DIR = Path.home() / ".codex" / "sessions"

# 단가표 ($/1M tokens) — 계측설계.md §2와 동기 유지, 업로드 전날 재확인
PRICING = {
    # model prefix: (input, cached_input, output)
    "gpt-5.6-sol":   (5.00, 0.50, 30.00),
    "gpt-5.6-terra": (2.50, 0.25, 15.00),
    "gpt-5.6-luna":  (1.00, 0.10, 6.00),
    # 참고용 (테스트 환경 검증에 쓰인 기존 모델은 비용 0 처리하지 않고 미지 단가로 표시)
}


def price_for(model: str):
    for prefix, p in PRICING.items():
        if model and model.startswith(prefix):
            return p
    return None


def ts(s: str) -> datetime:
    return datetime.fromisoformat(s.replace("Z", "+00:00"))


def parse_rollout(path: Path):
    """rollout jsonl 하나 → 턴 레코드 리스트."""
    session_id = None
    cwd = None
    model = effort = None
    turn_start = None
    first_response = None
    last_usage = None
    rate = {}
    turn_idx = 0
    interventions = 0  # request_user_input + exec_approval_request (자율 완주 축)
    goal_set = False   # thread_goal_updated 관측 여부
    rows = []

    for line in path.open():
        try:
            e = json.loads(line)
        except json.JSONDecodeError:
            continue
        t = e.get("type")
        p = e.get("payload") or {}
        when = e.get("timestamp")

        if t == "session_meta":
            session_id = p.get("session_id") or p.get("id")
            cwd = p.get("cwd")
        elif t == "turn_context":
            model = p.get("model")
            effort = p.get("effort")
            cwd = p.get("cwd") or cwd
        elif t == "event_msg":
            pt = p.get("type")
            if pt in ("user_message", "task_started"):
                if turn_start is None:  # user_message가 먼저 오면 그것이 시작
                    turn_start = when
                first_response = None
            elif pt in ("request_user_input", "exec_approval_request",
                        "request_permissions", "elicitation_request"):
                interventions += 1
            elif pt == "thread_goal_updated":
                goal_set = True
            elif pt == "agent_message" and first_response is None:
                first_response = when
            elif pt == "token_count":
                info = p.get("info") or {}
                last_usage = info.get("last_token_usage") or {}
                rl = p.get("rate_limits") or {}
                rate = {
                    "used_5h": (rl.get("primary") or {}).get("used_percent"),
                    "used_weekly": (rl.get("secondary") or {}).get("used_percent"),
                }
            elif pt == "task_complete":
                turn_idx += 1
                u = last_usage or {}
                inp = u.get("input_tokens", 0)
                cached = u.get("cached_input_tokens", 0)
                out = u.get("output_tokens", 0)
                reasoning = u.get("reasoning_output_tokens", 0)
                pr = price_for(model or "")
                cost = (
                    ((inp - cached) * pr[0] + cached * pr[1] + out * pr[2]) / 1e6
                    if pr else None
                )
                wall = (
                    (ts(when) - ts(turn_start)).total_seconds()
                    if turn_start and when else None
                )
                first_s = (
                    (ts(first_response) - ts(turn_start)).total_seconds()
                    if turn_start and first_response else None
                )
                rows.append({
                    "session_id": session_id,
                    "cwd": cwd,
                    "combo": Path(cwd).name if cwd else "",
                    "model": model,
                    "effort": effort,
                    "turn_idx": turn_idx,
                    "turn_start": turn_start,
                    "turn_end": when,
                    "wall_s": round(wall, 1) if wall is not None else "",
                    "first_response_s": round(first_s, 1) if first_s is not None else "",
                    "input_tokens": inp,
                    "cached_input_tokens": cached,
                    "output_tokens": out,
                    "reasoning_tokens": reasoning,
                    "reasoning_share": round(reasoning / out, 3) if out else "",
                    "cost_usd": round(cost, 6) if cost is not None else "",
                    "used_5h_pct": rate.get("used_5h", ""),
                    "used_weekly_pct": rate.get("used_weekly", ""),
                    "interventions": interventions,
                    "goal_mode": goal_set,
                })
                turn_start = None
                last_usage = None
                interventions = 0
    return rows


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--since", help="ISO 시각 이후 세션만 (예: 2026-07-11T19:00)")
    ap.add_argument("--cwd-filter", help="cwd에 이 문자열을 포함한 세션만")
    ap.add_argument("-o", "--output", help="CSV 저장 경로 (생략 시 stdout 표)")
    args = ap.parse_args()

    since = None
    if args.since:
        since = datetime.fromisoformat(args.since)
        if since.tzinfo is None:
            since = since.astimezone()  # 로컬 타임존 부여

    rows = []
    for f in sorted(SESSIONS_DIR.rglob("rollout-*.jsonl")):
        if since:
            try:  # 디렉토리 구조: sessions/YYYY/MM/DD/rollout-*.jsonl (일 단위 필터)
                y, m, d = f.parent.parts[-3:]
                file_day = datetime(int(y), int(m), int(d)).astimezone()
                if file_day.date() < since.date():
                    continue
            except (ValueError, IndexError):
                pass  # 구조가 다르면 내용으로 판단
        recs = parse_rollout(f)
        if args.cwd_filter:
            recs = [r for r in recs if args.cwd_filter in (r["cwd"] or "")]
        rows.extend(recs)

    if not rows:
        print("(추출된 턴 없음)", file=sys.stderr)
        return

    fields = list(rows[0].keys())
    if args.output:
        with open(args.output, "w", newline="") as fp:
            w = csv.DictWriter(fp, fieldnames=fields)
            w.writeheader()
            w.writerows(rows)
        print(f"{len(rows)} turns → {args.output}", file=sys.stderr)
    else:
        w = csv.DictWriter(sys.stdout, fieldnames=fields)
        w.writeheader()
        w.writerows(rows)


if __name__ == "__main__":
    main()
