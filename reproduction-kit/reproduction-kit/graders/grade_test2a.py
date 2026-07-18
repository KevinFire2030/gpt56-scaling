#!/usr/bin/env python3
"""②-A 함정 매출 분석 채점기 (보조 — 키워드 휴리스틱 + 수동 확정).

사용법: python3 grade_test2a.py --run-dir test2a/<combo>
recall은 키워드 매칭으로 잠정 산출하고, 최종 확정은 사람이 report.md를 읽고 조정한다
(휴리스틱 오판 방지 — 결과 JSON의 provisional=true 표기).
evaluator 통과(라우터용): recall ≥ 4/7 and 오탐 휴리스틱 ≤ 1
"""
import argparse
import re
import subprocess
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import emit, fail

# 함정별 (필수 키워드 세트 — 하나의 세트라도 전부 매칭되면 발견으로 판정)
TRAPS = {
    "T1_중복": [["중복"], ["이중", "적재"], ["duplicate"]],
    "T2_단위": [["부산", "단위"], ["천원", "단위"], ["1/1000"], ["단위", "혼재"]],
    "T3_단절": [["홍대", "누락"], ["홍대", "공백"], ["홍대", "단절"], ["홍대", "리뉴얼"]],
    "T4_심슨": [["심슨"], ["simpson"], ["객단가", "역설"], ["객단가", "믹스"],
                ["전체", "상승", "지점", "하락"]],
    "T5_요일": [["금요일", "프로모"], ["요일", "효과"], ["교락"], ["요일", "혼재"],
                ["promo", "금요일"]],
    "T6_스파이크": [["스파이크"], ["이상치"], ["100배"], ["전산", "오류"], ["outlier"]],
}
BAIT_CAUSAL = [["기온", "때문"], ["기온", "인과"], ["날씨", "영향", "증가"],
               ["온도", "매출", "원인"]]
BAIT_GOOD = [["기온", "상관", "인과"], ["기온", "주의"], ["온도", "혼동"],
             ["기온", "계절성"]]
WEIGHT = {"T1_중복": 1, "T2_단위": 1, "T3_단절": 1.5, "T4_심슨": 2.5,
          "T5_요일": 2.5, "T6_스파이크": 1}


def hit(text, groups):
    return any(all(k.lower() in text for k in g) for g in groups)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    args = ap.parse_args()
    run = Path(args.run_dir)
    rp = run / "report.md"
    if not rp.exists():
        return fail("test2a", "report.md 없음")
    text = rp.read_text().lower()

    # 형식 게이트
    has_table = bool(re.search(r"\|.*발견.*\|", text)) or text.count("|") >= 8
    code = run / "analysis.py"
    code_runs = None
    if code.exists():
        r = subprocess.run([sys.executable, str(code)], cwd=run,
                           capture_output=True, timeout=180)
        code_runs = r.returncode == 0

    found = {t: hit(text, g) for t, g in TRAPS.items()}
    recall = sum(found.values())
    weighted = sum(WEIGHT[t] for t, ok in found.items() if ok)
    bait_trapped = hit(text, BAIT_CAUSAL) and not hit(text, BAIT_GOOD)
    bait_handled = hit(text, BAIT_GOOD)

    score = (10 * has_table + 10 * bool(code_runs)
             + 60 * (weighted / sum(WEIGHT.values()))
             + 10 * bait_handled - 10 * bait_trapped)
    return emit({
        "test": "test2a", "run_dir": str(run), "provisional": True,
        "gates": {"summary_table": has_table, "analysis_py_runs": code_runs,
                  "trap_recall": f"{recall}/6", "traps_found": found,
                  "bait_T7": "오탐(인과 주장)" if bait_trapped
                             else ("가점(인과 없음 지적)" if bait_handled else "미언급"),
                  "weighted_recall": round(weighted, 1)},
        "score_auto": round(max(0, score), 1),
        "evaluator_pass": bool(recall >= 4 and not bait_trapped),
        "note": "키워드 휴리스틱 잠정치 — 최종 recall/오탐은 report.md 수동 검토로 확정",
    })


if __name__ == "__main__":
    sys.exit(main())
