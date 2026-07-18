#!/usr/bin/env python3
"""③-A 달 착지 비교 시뮬레이터 채점기 — 헤드리스 실행 + 중력 검산.

사용법: env -u PLAYWRIGHT_BROWSERS_PATH python3 grade_test3a.py --run-dir <combo dir>
게이트: G1 렌더(에러 0 + DANTE LABS 로고 존재) · G2 중력 검산 · G3 실험 조작 · (G4 먼지는 수동)
검산 기준 (프롬프트 무노출, 물리 상수에서 유도):
  낙하 시간비  moon/earth = √(9.81/1.62) ≈ 2.4607  (±5%)
  점프 높이비  moon/earth = 9.81/1.62  ≈ 6.0556  (±5%)
로그 형식(봉인 objective 요구 8): [EARTH]/[MOON] jump_apex_m=… / fall_time_s=… / landed
evaluator 통과: G1 and G2
"""
import argparse
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import emit, fail

RATIO_FALL = (9.81 / 1.62) ** 0.5   # ≈ 2.4607
RATIO_JUMP = 9.81 / 1.62            # ≈ 6.0556
TOL = 0.05
NUM = r"(-?\d+(?:\.\d+)?(?:e[+-]?\d+)?)"


def within(got, want, tol=TOL):
    return abs(got - want) / want <= tol


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--seconds", type=int, default=8, help="실험 후 로그 대기 시간")
    args = ap.parse_args()
    run = Path(args.run_dir)
    html = run / "index.html"
    if not html.exists():
        return fail("test3a", "index.html 없음")

    from playwright.sync_api import sync_playwright
    logs, errors = [], []
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome", headless=True)
        pg = b.new_page(viewport={"width": 1440, "height": 810})
        pg.on("console", lambda m: (errors if m.type == "error" else logs).append(m.text))
        pg.goto(html.resolve().as_uri(), timeout=60000)
        pg.wait_for_timeout(3000)
        body = pg.inner_text("body")
        # 실험 트리거: 점프/낙하 버튼을 텍스트 휴리스틱으로 클릭
        clicked = []
        for kw in ("점프", "jump", "낙하", "drop", "fall"):
            try:
                loc = pg.get_by_role("button", name=re.compile(kw, re.I)).first
                loc.click(timeout=2500)
                clicked.append(kw)
                pg.wait_for_timeout(args.seconds * 1000 // 2)
            except Exception:
                continue
        b.close()

    # 로고는 WebGL 캔버스 텍스처로 그려져 DOM 텍스트 검사로는 검출 불가(2026-07-12 Fable5
    # 드라이런에서 확인). 그리려면 소스에 문자열이 있어야 하므로 소스 검사로 판정하고,
    # 실제 화면 가독성은 G4와 함께 수동 프레임 관찰로 확정한다.
    src = html.read_text(encoding="utf-8", errors="ignore").upper()
    logo_ok = ("DANTE" in src and "LABS" in src) or "DANTE LABS" in body.upper() \
        or any("DANTE" in l.upper() for l in logs)

    def grab(tag, key):
        vals = []
        for l in logs:
            if tag in l.upper() and key in l:
                m = re.search(key + r"\s*[=:]\s*" + NUM, l)
                if m:
                    vals.append(float(m.group(1)))
        return vals

    fall_e, fall_m = grab("EARTH", "fall_time_s"), grab("MOON", "fall_time_s")
    apex_e, apex_m = grab("EARTH", "jump_apex_m"), grab("MOON", "jump_apex_m")

    checks = {}
    if fall_e and fall_m and fall_e[-1] > 0:
        got = fall_m[-1] / fall_e[-1]
        checks["fall_ratio"] = {"got": round(got, 3), "want": round(RATIO_FALL, 3),
                                "ok": within(got, RATIO_FALL)}
    if apex_e and apex_m and apex_e[-1] > 0:
        got = apex_m[-1] / apex_e[-1]
        checks["jump_ratio"] = {"got": round(got, 3), "want": round(RATIO_JUMP, 3),
                                "ok": within(got, RATIO_JUMP)}

    g1 = len(errors) == 0 and logo_ok
    g2 = bool(checks) and all(v["ok"] for v in checks.values())
    g3 = len(clicked) >= 2

    score = (20 * (len(errors) == 0) + 10 * logo_ok
             + 40 * (sum(v["ok"] for v in checks.values()) / 2 if checks else 0)
             + 15 * g3 + 15 * (len(logs) > 0))
    return emit({
        "test": "test3a", "run_dir": str(run),
        "gates": {"G1_render": g1, "console_errors": errors[:5],
                  "logo_dantelabs": logo_ok,  # 소스 휴리스틱 — 화면 가독성은 수동 확정

                  "G2_gravity_checks": checks or "측정 불가(로그 미확보 — 수동 실행 필요)",
                  "G3_buttons_clicked": clicked,
                  "log_count": len(logs)},
        "sample_logs": [l for l in logs if "EARTH" in l.upper() or "MOON" in l.upper()][:6],
        "score_auto": round(max(0, score), 1),
        "evaluator_pass": bool(g1 and g2),
        "note": "G4(먼지 진공 탄도·발자국)는 수동 프레임 관찰로 판정. 버튼 클릭 실패 시 VERIFICATION.md의 자가 기록 로그로 대체 검산 가능.",
    })


if __name__ == "__main__":
    sys.exit(main())
