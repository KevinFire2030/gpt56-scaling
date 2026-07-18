#!/usr/bin/env python3
"""테스트 ④ — 자동 승급 라우팅 파이프라인.

체제 3종을 같은 과제 큐에 돌려 성공률·비용을 비교한다:
  A) --regime sol-high    : 전부 Sol High (돈으로 미는 체제)
  B) --regime luna-medium : 전부 Luna Medium (아끼다 망하는 체제)
  C) --regime auto        : 난도 분류(Luna Low) → 초기 배분 → 실패 시 승급 2단

사용법:
  python3 run_router.py --regime auto --tasks test1a,test1b,test2a --out router_runs/auto
  (과제 자산은 deploy_assets.sh로 해당 폴더에 미리 배포돼 있어야 함)

승급 사다리 (프롬프트.md ④ 봉인):
  simple → luna/medium,  medium → terra/high,  hard → sol/high
  evaluator 실패 시: terra/high → sol/max (최종)

실행 엔진: codex exec (YOLO) — rollout이 남으므로 비용·시간은 collect_metrics.py로 사후 집계.
"""
import argparse
import json
import re
import shutil
import subprocess
import sys
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
GRADERS = BASE / "scripts" / "graders"

# 과제 정의: (자산 소스 폴더, objective 파일, 채점기, 채점 대상 파일들)
TASKS = {
    "test1a": {"assets": BASE / "test1" / "receipts", "glob": "R*.png",
               "grader": "grade_test1a.py"},
    "test1b": {"assets": BASE / "test1b", "glob": "*.xlsx",
               "grader": "grade_test1b.py"},
    "test2a": {"assets": BASE / "test2a", "glob": "sales.csv",
               "grader": "grade_test2a.py"},
    "test2b": {"assets": None, "glob": None, "grader": "grade_test2b.py"},
    "test2c": {"assets": BASE / "test2c", "glob": "*.md",
               "grader": "grade_test2c.py"},
    "test3a": {"assets": None, "glob": None, "grader": "grade_test3a.py"},
    "test3b": {"assets": BASE / "test3b", "glob": "TOOLS.md",
               "grader": "grade_test3b.py"},
}

CLASSIFY_PROMPT = """아래 작업 요청을 읽고 난도를 분류해 주세요. 다른 설명 없이 JSON 하나만 출력합니다.

{{ "difficulty": "simple | medium | hard", "reason": "한 문장" }}

분류 기준:
- simple: 출력 형식이 정해져 있고 정답을 기계적으로 검증할 수 있는 작업
- medium: 데이터를 해석하거나 판단이 필요하지만 산출물 구조가 명확한 작업
- hard: 설계 판단이 필요하거나 여러 요구사항을 동시에 만족해야 하는 제작 작업

[작업 요청]
{task}"""

INITIAL = {"simple": ("gpt-5.6-luna", "medium"),
           "medium": ("gpt-5.6-terra", "high"),
           "hard": ("gpt-5.6-sol", "high")}
ESCALATE_TO = ("gpt-5.6-sol", "max")  # 실패 시 최종 승급


def codex_exec(model, effort, prompt, cwd):
    cmd = ["codex", "exec", "--dangerously-bypass-approvals-and-sandbox",
           "-m", model, "-c", f"model_reasoning_effort={effort}",
           "--cd", str(cwd), prompt]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=3600)
    return r.returncode == 0, r.stdout[-2000:]


def load_objective(task):
    """프롬프트.md에서 해당 테스트의 봉인 objective 코드블록을 추출."""
    md = (BASE / "프롬프트.md").read_text()
    labels = {"test1a": "①-A", "test1b": "①-B", "test2a": "②-A",
              "test2b": "②-B", "test2c": "②-C", "test3a": "③-A", "test3b": "③-B"}
    sec = re.search(rf"## 테스트 {re.escape(labels[task])}.*?```\n(.*?)```", md, re.S)
    if not sec:
        raise RuntimeError(f"{task} objective 추출 실패 — 프롬프트.md 구조 확인")
    return sec.group(1).strip()


def grade(task, run_dir):
    cmd = [sys.executable, str(GRADERS / TASKS[task]["grader"]), "--run-dir", str(run_dir)]
    env_prefix = []
    r = subprocess.run(cmd, capture_output=True, text=True,
                       env={**__import__("os").environ, "PLAYWRIGHT_BROWSERS_PATH": ""})
    try:
        return json.loads(r.stdout)
    except json.JSONDecodeError:
        return {"evaluator_pass": False, "error": r.stdout[-500:] or r.stderr[-500:]}


def classify(objective, cwd):
    ok, out = codex_exec("gpt-5.6-luna", "low", CLASSIFY_PROMPT.format(task=objective), cwd)
    m = re.search(r'"difficulty"\s*:\s*"(simple|medium|hard)"', out)
    return m.group(1) if m else "medium"


def prepare_dir(task, out_root, attempt):
    d = out_root / task / f"attempt{attempt}"
    d.mkdir(parents=True, exist_ok=True)
    spec = TASKS[task]
    if spec["assets"]:
        for f in spec["assets"].glob(spec["glob"]):
            shutil.copy2(f, d)
    return d


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--regime", required=True, choices=["sol-high", "luna-medium", "auto"])
    ap.add_argument("--tasks", default="test1a,test1b,test2a,test2b,test2c,test3a")
    ap.add_argument("--out", required=True)
    args = ap.parse_args()
    out_root = Path(args.out)
    results = []

    for task in args.tasks.split(","):
        task = task.strip()
        objective = load_objective(task)
        log = {"task": task, "regime": args.regime, "attempts": []}

        if args.regime == "sol-high":
            plan = [("gpt-5.6-sol", "high")]
        elif args.regime == "luna-medium":
            plan = [("gpt-5.6-luna", "medium")]
        else:  # auto — 분류 후 배분, 실패 시 승급
            wd0 = prepare_dir(task, out_root, 0)
            diff = classify(objective, wd0)
            log["classified"] = diff
            plan = [INITIAL[diff], ESCALATE_TO]

        verdict = None
        for i, (model, effort) in enumerate(plan, 1):
            wd = prepare_dir(task, out_root, i)
            print(f"[{task}] attempt{i}: {model}/{effort}", flush=True)
            codex_exec(model, effort, objective, wd)
            verdict = grade(task, wd)
            log["attempts"].append({"model": model, "effort": effort,
                                    "pass": verdict.get("evaluator_pass"),
                                    "score": verdict.get("score_auto")})
            if verdict.get("evaluator_pass"):
                break  # 통과 → 승급 불필요
        log["final_pass"] = verdict.get("evaluator_pass") if verdict else False
        results.append(log)
        print(f"[{task}] 최종: {'PASS' if log['final_pass'] else 'FAIL'} "
              f"({len(log['attempts'])}회 시도)", flush=True)

    out_root.mkdir(parents=True, exist_ok=True)
    (out_root / "router_result.json").write_text(
        json.dumps(results, ensure_ascii=False, indent=2))
    n_pass = sum(r["final_pass"] for r in results)
    print(f"\n체제 {args.regime}: {n_pass}/{len(results)} 성공 "
          f"→ 비용·시간은 collect_metrics.py --since <시작시각> 로 집계")


if __name__ == "__main__":
    main()
