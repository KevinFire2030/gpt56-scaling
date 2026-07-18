#!/usr/bin/env python3
"""테스트 ① '영수증 지옥' — 정답지 생성 + gpt-image-2 더미 영수증 이미지 20장 생성.

원칙: 정답지(ground truth)를 먼저 확정하고, 그 데이터를 프롬프트에 박아 이미지를 만든다.
함정 배치 (평가설계.md ①):
  - 합계 불일치 3장: R04(total +1000), R11(subtotal 오기), R17(tax 오기)
  - 단위 혼재: R07(천원 단위 표기), R14(영문 상호 + KRW 표기)
  - 항목명 오타: R06(아메리카노노), R13(불고기버거셋트)
  - 판독 불가: R19(커피 얼룩으로 감자튀김 수량 가림)

사용법:
  python3 gen_receipt_images.py --ground-truth-only   # 정답지 JSON만 생성
  python3 gen_receipt_images.py                        # 정답지 + 이미지 20장 생성
  python3 gen_receipt_images.py --only R04,R11         # 특정 장만 재생성
"""
import argparse
import json
import shutil
import subprocess
import sys
import time
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent
OUT_DIR = BASE / "test1" / "receipts"
KIE_CLI = Path.home() / ".claude/skills/kie-image-generator/scripts/generate_image.py"

# ---------------------------------------------------------------------------
# 정답 데이터 (subtotal/tax/total은 코드가 계산 — 수기 산수 오류 차단)
# trap: total_delta / subtotal_delta / tax_delta = 인쇄값을 정답에서 이만큼 비틀기
# currency: 금액 표기 스타일 (won=원, sym=₩, krw=KRW, chon=천원 단위 소수 표기)
# ---------------------------------------------------------------------------
RECEIPTS = [
    {"id": "R01", "store": "카페 한잔의 여유", "date": "2026-06-02", "currency": "won",
     "items": [("아메리카노", 2, 4500), ("크루아상", 1, 3800)]},
    {"id": "R02", "store": "다온분식", "date": "2026-06-03", "currency": "sym",
     "items": [("떡볶이", 1, 5000), ("김말이", 2, 1500), ("어묵", 3, 1000)]},
    {"id": "R03", "store": "GS편의점 서초점", "date": "2026-06-05", "currency": "won",
     "items": [("삼각김밥", 2, 1200), ("바나나우유", 1, 1700)]},
    {"id": "R04", "store": "명동칼국수", "date": "2026-06-06", "currency": "won",
     "items": [("칼국수", 2, 9000), ("만두", 1, 7000)], "total_delta": 1000,
     "expected_flag": "합계 불일치 (인쇄 total이 소계+부가세보다 1,000원 큼)"},
    {"id": "R05", "store": "스시혼마", "date": "2026-06-08", "currency": "won",
     "items": [("모둠초밥", 1, 18000), ("미소시루", 1, 2000)]},
    {"id": "R06", "store": "커피빈스 강남", "date": "2026-06-09", "currency": "won",
     "items": [("아메리카노노", 1, 5100), ("카페라떼", 2, 5600)],
     "note": "품목명 오타(아메리카노노)는 인쇄된 그대로 추출해야 정답"},
    {"id": "R07", "store": "한우정육식당", "date": "2026-06-10", "currency": "chon",
     "items": [("등심 150g", 2, 45000), ("된장찌개", 1, 8000)],
     "expected_flag": "금액이 천원 단위 표기 — 원 단위 환산 필요"},
    {"id": "R08", "store": "파리바게뜨 역삼점", "date": "2026-06-11", "currency": "won",
     "items": [("소보로빵", 3, 2200), ("우유식빵", 1, 3900)]},
    {"id": "R09", "store": "교촌치킨 서초점", "date": "2026-06-12", "currency": "won",
     "items": [("허니콤보", 1, 23000), ("콜라 1.25L", 1, 3000)]},
    {"id": "R10", "store": "올리브영 강남본점", "date": "2026-06-13", "currency": "won",
     "items": [("선크림", 1, 18900), ("립밤", 2, 6500)]},
    {"id": "R11", "store": "홍콩반점 서초", "date": "2026-06-15", "currency": "won",
     "items": [("짜장면", 2, 7000), ("탕수육(소)", 1, 15000)], "subtotal_delta": -2000,
     "expected_flag": "품목 합계(29,000)와 인쇄 소계(27,000) 불일치"},
    {"id": "R12", "store": "스타벅스 R점", "date": "2026-06-16", "currency": "won",
     "items": [("콜드브루", 2, 5800), ("치즈케이크", 1, 7300)]},
    {"id": "R13", "store": "맘터치 서초역점", "date": "2026-06-17", "currency": "won",
     "items": [("불고기버거셋트", 2, 8900), ("케이준감자", 1, 3400)],
     "note": "품목명 오타(셋트)는 인쇄된 그대로 추출해야 정답"},
    {"id": "R14", "store": "The Bread Lab", "date": "2026-06-18", "currency": "krw",
     "items": [("Sourdough", 1, 7500), ("Butter Croissant", 2, 4200)],
     "expected_flag": "영문 영수증 + KRW 표기 — 원 단위 정수 환산"},
    {"id": "R15", "store": "김밥천국 교대점", "date": "2026-06-19", "currency": "won",
     "items": [("참치김밥", 2, 4500), ("라볶이", 1, 6000)]},
    {"id": "R16", "store": "이마트24 방배점", "date": "2026-06-20", "currency": "won",
     "items": [("생수 2L", 2, 1400), ("컵라면", 3, 1300)]},
    {"id": "R17", "store": "본죽 서초점", "date": "2026-06-22", "currency": "won",
     "items": [("전복죽", 1, 12000), ("소고기죽", 1, 10500)], "tax_delta": -1000,
     "expected_flag": "부가세 오기(1,250 → 실제 2,250) — 합계 검산 불일치"},
    {"id": "R18", "store": "배스킨라빈스 서초점", "date": "2026-06-23", "currency": "won",
     "items": [("파인트", 1, 9800), ("싱글콘", 2, 4000)]},
    {"id": "R19", "store": "동네수제버거", "date": "2026-06-25", "currency": "won",
     "items": [("치즈버거", 2, 8500), ("감자튀김", 1, 4500)], "stain": "감자튀김 수량",
     "expected_flag": "커피 얼룩으로 감자튀김 수량 판독 불가 — null 처리"},
    {"id": "R20", "store": "다이소 서초점", "date": "2026-06-26", "currency": "won",
     "items": [("건전지 AA", 2, 3000), ("수납박스", 1, 5000)]},
]


def fmt_money(v: int, currency: str) -> str:
    if currency == "chon":  # 천원 단위 소수 표기 (예: 45.0)
        return f"{v / 1000:.1f}"
    if currency == "sym":
        return f"₩{v:,}"
    if currency == "krw":
        return f"{v:,} KRW"
    return f"{v:,}원"


def compute(r: dict) -> dict:
    """정답값과 인쇄값(함정 반영)을 계산."""
    items = [
        {"name": n, "qty": q, "unit_price": p, "amount": q * p}
        for n, q, p in r["items"]
    ]
    subtotal = sum(i["amount"] for i in items)
    tax = round(subtotal * 0.1)
    printed_subtotal = subtotal + r.get("subtotal_delta", 0)
    printed_tax = tax + r.get("tax_delta", 0)
    printed_total = printed_subtotal + printed_tax + r.get("total_delta", 0)
    return {
        "receipt_id": r["id"], "store_name": r["store"], "date": r["date"],
        "currency_style": r["currency"], "items": items,
        "true_subtotal": subtotal, "true_tax": tax, "true_total": subtotal + tax,
        "printed_subtotal": printed_subtotal, "printed_tax": printed_tax,
        "printed_total": printed_total,
        "expected_flag": r.get("expected_flag"), "note": r.get("note"),
        "stain": r.get("stain"),
    }


def build_prompt(g: dict) -> str:
    c = g["currency_style"]
    lines = []
    for i in g["items"]:
        qty = i["qty"]
        if g.get("stain") and g["stain"].startswith(i["name"][:3]):
            qty_str = "(qty hidden under stain)"
        else:
            qty_str = str(qty)
        lines.append(
            f"  {i['name']}  x{qty_str}  {fmt_money(i['unit_price'], c)}  {fmt_money(i['amount'], c)}"
        )
    body = "\n".join(lines)
    unit_note = (
        ' A small header note reads "금액단위: 천원".' if c == "chon" else ""
    )
    stain_note = (
        f' A realistic brown coffee ring stain partially covers the quantity of the last item line, making that number unreadable.'
        if g.get("stain") else ""
    )
    return (
        "Photorealistic flatbed scan of a Korean thermal paper store receipt, "
        "portrait orientation, slightly tilted about 3 degrees, mild paper crumples, "
        "faint dot-matrix font, white paper with light gray shading."
        f"{unit_note}{stain_note} "
        "The receipt must display EXACTLY this text, no other items or numbers:\n"
        f"[{g['store_name']}]\n"
        f"일자: {g['date']}\n"
        "--------------------------------\n"
        "품목      수량   단가      금액\n"
        f"{body}\n"
        "--------------------------------\n"
        f"공급가액: {fmt_money(g['printed_subtotal'], c)}\n"
        f"부가세: {fmt_money(g['printed_tax'], c)}\n"
        f"합계: {fmt_money(g['printed_total'], c)}\n"
        "--------------------------------\n"
        "감사합니다. 또 오세요!\n"
        "All Korean text must be spelled exactly as given, digits must match exactly."
    )


def generate_image(g: dict, out_dir: Path) -> bool:
    tmp = out_dir / "_tmp"
    if tmp.exists():
        shutil.rmtree(tmp)
    tmp.mkdir(parents=True)
    cmd = [
        sys.executable, str(KIE_CLI), build_prompt(g),
        "--model", "gpt-image-2", "--aspect-ratio", "2:3", "--size", "2K",
        "-y", "-o", str(tmp),
    ]
    r = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
    imgs = sorted(tmp.glob("*.png")) + sorted(tmp.glob("*.jpg")) + sorted(tmp.glob("*.jpeg")) + sorted(tmp.glob("*.webp"))
    if r.returncode != 0 or not imgs:
        print(f"[{g['receipt_id']}] FAIL rc={r.returncode}\n{r.stdout[-400:]}\n{r.stderr[-400:]}", flush=True)
        return False
    dest = out_dir / f"{g['receipt_id']}{imgs[0].suffix}"
    shutil.move(str(imgs[0]), dest)
    shutil.rmtree(tmp, ignore_errors=True)
    print(f"[{g['receipt_id']}] OK → {dest.name}", flush=True)
    return True


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--ground-truth-only", action="store_true")
    ap.add_argument("--only", help="특정 ID만 재생성 (쉼표 구분, 예: R04,R11)")
    args = ap.parse_args()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    truths = [compute(r) for r in RECEIPTS]

    gt_path = OUT_DIR / "ground_truth.json"
    gt_path.write_text(json.dumps(truths, ensure_ascii=False, indent=2))
    print(f"정답지 → {gt_path} ({len(truths)}장)", flush=True)

    if args.ground_truth_only:
        return

    targets = truths
    if args.only:
        ids = {x.strip().upper() for x in args.only.split(",")}
        targets = [g for g in truths if g["receipt_id"] in ids]

    ok = 0
    for g in targets:
        if generate_image(g, OUT_DIR):
            ok += 1
        time.sleep(2)  # API 예의
    print(f"완료: {ok}/{len(targets)}", flush=True)


if __name__ == "__main__":
    main()
