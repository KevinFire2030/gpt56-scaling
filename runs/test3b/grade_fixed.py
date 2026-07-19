import argparse
import json
import subprocess
import sys
from pathlib import Path


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    args = ap.parse_args()
    grader = Path(__file__).resolve().parents[1] / ".." / "reproduction-kit" / "reproduction-kit" / "graders" / "grade_test3b.py"
    original = grader.resolve().read_text(encoding="utf-8")
    fixed = original.replace(
        "+ 10 * (has_mg and lines and max(lines) >= 8))",
        "+ 10 * bool(has_mg and lines and max(lines) >= 8))",
    )
    tmp = grader.with_name("_grade_test3b_fixed_tmp.py")
    tmp.write_text(fixed, encoding="utf-8")
    try:
        proc = subprocess.run(
            [sys.executable, str(tmp), "--run-dir", args.run_dir],
            text=True,
            capture_output=True,
        )
    finally:
        tmp.unlink(missing_ok=True)
    if proc.stdout:
        print(proc.stdout, end="")
    if proc.stderr:
        print(proc.stderr, file=sys.stderr, end="")
    if proc.returncode != 0:
        print(json.dumps({
            "test": "test3b",
            "run_dir": args.run_dir,
            "score_auto": 0,
            "evaluator_pass": False,
            "grader_error": proc.stderr.strip() or f"returncode {proc.returncode}",
        }, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
