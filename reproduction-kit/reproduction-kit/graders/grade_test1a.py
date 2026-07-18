#!/usr/bin/env python3
"""①-A 영수증 추출 채점기.

사용법: python3 grade_test1a.py --run-dir test1/<combo>
게이트: G1 스키마 · G2 필드 정확도 ≥95% · G3 불일치 3장 플래그 · (G4 단위 정규화는 필드 정확도에 포함)
evaluator 통과: G1 and 필드 정확도 ≥ 95%
"""
import argparse
import json
import re
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import emit, fail

BASE = Path(__file__).resolve().parent.parent.parent
GT_PATH = BASE / "test1" / "receipts" / "ground_truth.json"
MISMATCH_IDS = {"R04", "R11", "R17"}          # 합계 불일치 함정
LEGIT_FLAG_IDS = MISMATCH_IDS | {"R07", "R14", "R19"}  # 플래그가 정당한 장

REQUIRED = ["receipt_id", "store_name", "date", "items", "subtotal", "tax", "total", "flags"]


def norm_id(rid):
    m = re.search(r"(\d+)", str(rid or ""))
    return f"R{int(m.group(1)):02d}" if m else None


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--file", default="receipts.json")
    args = ap.parse_args()
    run = Path(args.run_dir)

    gt = {g["receipt_id"]: g for g in json.loads(GT_PATH.read_text())}

    # G1 — 스키마/형식
    f = run / args.file
    if not f.exists():
        return fail("test1a", f"{args.file} 없음")
    try:
        data = json.loads(f.read_text())
    except json.JSONDecodeError as e:
        return fail("test1a", f"JSON 파싱 실패: {e}")
    if not isinstance(data, list) or len(data) != 20:
        return fail("test1a", f"배열 20개 아님 (={len(data) if isinstance(data, list) else type(data)})")
    schema_ok = all(all(k in r for k in REQUIRED) for r in data)

    # G2 — 필드 정확도 (printed 값 기준)
    total_fields = correct = 0
    per_receipt = {}
    for r in data:
        rid = norm_id(r.get("receipt_id"))
        g = gt.get(rid)
        if not g:
            continue
        checks = []
        checks.append(str(r.get("store_name", "")).strip() == g["store_name"])
        checks.append(str(r.get("date", "")).strip() == g["date"])
        checks.append(r.get("subtotal") == g["printed_subtotal"])
        checks.append(r.get("tax") == g["printed_tax"])
        checks.append(r.get("total") == g["printed_total"])
        gt_items = {i["name"]: i for i in g["items"]}
        for it in (r.get("items") or []):
            gi = gt_items.get(str(it.get("name", "")).strip())
            if gi is None:
                checks.append(False)
                continue
            qty_ok = it.get("qty") == gi["qty"]
            if g.get("stain") and g["stain"].startswith(str(it.get("name", ""))[:3]):
                qty_ok = it.get("qty") in (None, gi["qty"])  # 얼룩: null 허용
            checks += [qty_ok,
                       it.get("unit_price") == gi["unit_price"],
                       it.get("amount") == gi["amount"]]
        total_fields += len(checks)
        correct += sum(checks)
        per_receipt[rid] = f"{sum(checks)}/{len(checks)}"
    acc = correct / total_fields * 100 if total_fields else 0.0

    # G3 — 불일치 플래그 recall / 오탐
    KW = re.compile("합계|불일치|검산|맞지 않|오류|다릅")
    flagged = {norm_id(r["receipt_id"]) for r in data
               if any(KW.search(str(x)) for x in (r.get("flags") or []))}
    recall_hits = sorted(flagged & MISMATCH_IDS)
    false_flags = sorted({norm_id(r["receipt_id"]) for r in data if r.get("flags")}
                         - LEGIT_FLAG_IDS)

    score = (20 * schema_ok + 60 * (acc / 100)
             + 20 * (len(recall_hits) / 3) - 5 * len(false_flags))
    return emit({
        "test": "test1a", "run_dir": str(run),
        "gates": {"G1_schema": schema_ok, "G2_field_acc_pct": round(acc, 2),
                  "G3_mismatch_recall": f"{len(recall_hits)}/3 {recall_hits}",
                  "false_flags": false_flags},
        "per_receipt": per_receipt,
        "score_auto": round(max(0, score), 1),
        "evaluator_pass": bool(schema_ok and acc >= 95),
    })


if __name__ == "__main__":
    sys.exit(main())
