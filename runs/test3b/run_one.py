import json
import subprocess
import sys
import time
from pathlib import Path


def main() -> int:
    if len(sys.argv) != 2:
        print("usage: python run_one.py <profile>", file=sys.stderr)
        return 2

    root = Path(__file__).resolve().parents[2]
    profile = sys.argv[1]
    run = root / "runs" / "test3b" / profile
    run.mkdir(parents=True, exist_ok=True)
    prompt = (root / "runs" / "test3b" / "_prompt.txt").read_text(encoding="utf-8")

    start = time.time()
    rc = subprocess.run(
        ["hermes", "-p", profile, "--yolo", "-z", prompt, "--usage-file", ".\\usage.json"],
        cwd=run,
    ).returncode

    rec = {
        "profile": profile,
        "seconds": round(time.time() - start, 1),
        "html": (run / "index.html").exists(),
        "sources": (run / "SOURCES.md").exists(),
        "verification": (run / "VERIFICATION.md").exists(),
        "usage": (run / "usage.json").exists(),
        "returncode": rc,
        "finished_at": time.strftime("%Y-%m-%d %H:%M:%S"),
    }
    with (root / "runs" / "test3b" / "run_times.jsonl").open("a", encoding="utf-8") as f:
        f.write(json.dumps(rec, ensure_ascii=False) + "\n")
    print(json.dumps(rec, ensure_ascii=False))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
