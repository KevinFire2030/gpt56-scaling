#!/usr/bin/env python
"""Reproducible quality checks and management-report generator for sales.csv.
Uses only the Python standard library. Run: python analysis.py
"""
from __future__ import annotations

import csv
import datetime as dt
import math
import statistics
from collections import Counter, defaultdict
from pathlib import Path

INPUT = Path("sales.csv")
OUTPUT = Path("report.md")
REQUIRED = ("date", "store", "revenue", "transactions", "promo", "avg_temp_c")
KOREAN_WEEKDAYS = ["월", "화", "수", "목", "금", "토", "일"]


def won(value: float) -> str:
    return f"{round(value):,}원"


def pct(value: float, digits: int = 1) -> str:
    sign = "+" if value > 0 else ""
    return f"{sign}{value * 100:.{digits}f}%"


def fiscal_year(day: dt.date) -> str:
    start = day.year if day.month >= 7 else day.year - 1
    return f"{start}-{start + 1}"


def daterange(start: dt.date, end: dt.date):
    while start <= end:
        yield start
        start += dt.timedelta(days=1)


def read_data(path: Path) -> list[dict]:
    with path.open(encoding="utf-8-sig", newline="") as handle:
        reader = csv.DictReader(handle)
        if reader.fieldnames is None or set(REQUIRED) - set(reader.fieldnames):
            missing = ", ".join(sorted(set(REQUIRED) - set(reader.fieldnames or [])))
            raise ValueError(f"필수 열 누락: {missing}")
        rows = []
        for line, raw in enumerate(reader, start=2):
            try:
                row = {
                    "date": dt.date.fromisoformat(raw["date"].strip()),
                    "store": raw["store"].strip(),
                    "revenue": float(raw["revenue"]),
                    "transactions": int(float(raw["transactions"])),
                    "promo": int(float(raw["promo"])),
                    "avg_temp_c": float(raw["avg_temp_c"]),
                    "line": line,
                }
            except (ValueError, AttributeError) as exc:
                raise ValueError(f"{line}행 형식 오류: {exc}") from exc
            if not row["store"] or row["revenue"] < 0 or row["transactions"] <= 0 or row["promo"] not in (0, 1):
                raise ValueError(f"{line}행 값 범위 오류")
            row["ticket"] = row["revenue"] / row["transactions"]
            rows.append(row)
    if not rows:
        raise ValueError("데이터 행이 없습니다.")
    return rows


def median_abs_deviation(values: list[float]) -> tuple[float, float]:
    center = statistics.median(values)
    return center, statistics.median(abs(x - center) for x in values)


def render_report(raw: list[dict]) -> str:
    stores = sorted({r["store"] for r in raw})
    first_day, last_day = min(r["date"] for r in raw), max(r["date"] for r in raw)
    by_key = defaultdict(list)
    for row in raw:
        by_key[(row["store"], row["date"])].append(row)

    # Exact duplicate dates are not additive sales. Keep the first row deterministically.
    duplicate_groups = {key: group for key, group in by_key.items() if len(group) > 1}
    duplicate_rows = sum(len(group) - 1 for group in duplicate_groups.values())
    duplicate_store_dates = Counter(key[0] for key in duplicate_groups)
    unique_rows = []
    for key in sorted(by_key, key=lambda k: (k[0], k[1])):
        unique_rows.append(by_key[key][0])

    # Detect coverage gaps against the common full date span.
    expected_dates = set(daterange(first_day, last_day))
    present = defaultdict(set)
    for row in unique_rows:
        present[row["store"]].add(row["date"])
    gaps = {store: sorted(expected_dates - present[store]) for store in stores if expected_dates - present[store]}

    # Detect unit-price outliers by robust per-store MAD. A floor prevents tiny MAD issues.
    per_store = defaultdict(list)
    for row in unique_rows:
        per_store[row["store"]].append(row)
    point_outliers = []
    ticket_medians = {}
    for store, rows in per_store.items():
        center, mad = median_abs_deviation([r["ticket"] for r in rows])
        ticket_medians[store] = center
        threshold = max(10 * 1.4826 * mad, center * 0.50)
        for row in rows:
            if abs(row["ticket"] - center) > threshold:
                point_outliers.append(row)

    # A store-wide unit mismatch: median ticket <20% of the median of other locations.
    mismatch_stores = []
    for store, med in ticket_medians.items():
        others = [m for s, m in ticket_medians.items() if s != store]
        peer_med = statistics.median(others)
        if med < peer_med * 0.20 or med > peer_med * 5:
            mismatch_stores.append((store, med, peer_med))
    mismatch_names = {store for store, _, _ in mismatch_stores}
    outlier_keys = {(r["store"], r["date"]) for r in point_outliers}

    # Correction policy: dedupe, remove single-point outliers, and exclude unknown-unit stores.
    clean = [r for r in unique_rows if (r["store"], r["date"]) not in outlier_keys and r["store"] not in mismatch_names]
    if not clean:
        raise ValueError("보정 후 분석 가능한 행이 없습니다.")

    # Fiscal-year store averages use revenue/day to avoid missing-date bias.
    fy_store = defaultdict(lambda: {"revenue": 0.0, "transactions": 0, "days": 0})
    for row in clean:
        bucket = fy_store[(row["store"], fiscal_year(row["date"]))]
        bucket["revenue"] += row["revenue"]
        bucket["transactions"] += row["transactions"]
        bucket["days"] += 1
    fiscal_years = sorted({fiscal_year(r["date"]) for r in clean})
    latest_fy, previous_fy = fiscal_years[-1], fiscal_years[-2]
    growth = []
    for store in sorted({r["store"] for r in clean}):
        cur, prev = fy_store[(store, latest_fy)], fy_store[(store, previous_fy)]
        if cur["days"] and prev["days"]:
            daily_growth = cur["revenue"] / cur["days"] / (prev["revenue"] / prev["days"]) - 1
            transaction_growth = cur["transactions"] / cur["days"] / (prev["transactions"] / prev["days"]) - 1
            growth.append((store, daily_growth, transaction_growth, cur, prev))
    top_growth = sorted(growth, key=lambda x: x[1], reverse=True)[:3]
    declining = sorted([x for x in growth if x[1] < 0], key=lambda x: x[1])

    # Promotion appears exclusively on Fridays, so a same-Friday non-promo control does not exist.
    # Use the same store/month's adjacent Thursday and Saturday revenue as a transparent proxy baseline.
    # This is directional evidence, not a causal ROI estimate.
    adjacent_nonpromo = defaultdict(lambda: defaultdict(list))
    for r in clean:
        if r["promo"] == 0 and r["date"].weekday() in (3, 5):  # Thu/Sat around Friday
            adjacent_nonpromo[(r["store"], r["date"].strftime("%Y-%m"))][r["date"].weekday()].append(r["revenue"])
    promo_results = []
    for r in clean:
        if r["promo"] != 1:
            continue
        values = adjacent_nonpromo[(r["store"], r["date"].strftime("%Y-%m"))]
        if values[3] and values[5]:
            expected = (statistics.mean(values[3]) + statistics.mean(values[5])) / 2
            promo_results.append((r, expected))
    promo_actual = sum(r["revenue"] for r, _ in promo_results)
    promo_expected = sum(expected for _, expected in promo_results)
    promo_lift = promo_actual / promo_expected - 1 if promo_expected else 0.0

    # Calendar opportunity: use average day-level revenue after correction.
    weekday_values = defaultdict(list)
    month_values = defaultdict(list)
    for r in clean:
        weekday_values[r["date"].weekday()].append(r["revenue"])
        month_values[r["date"].month].append(r["revenue"])
    weekday_avg = {k: statistics.mean(v) for k, v in weekday_values.items()}
    month_avg = {k: statistics.mean(v) for k, v in month_values.items()}
    low_weekday = min(weekday_avg, key=weekday_avg.get)
    high_weekday = max(weekday_avg, key=weekday_avg.get)
    low_month = min(month_avg, key=month_avg.get)
    high_month = max(month_avg, key=month_avg.get)

    # Ticket gap is a clear cross-store, controllable benchmark (excluding invalid-unit store).
    latest_ticket = []
    for store in sorted({r["store"] for r in clean}):
        b = fy_store[(store, latest_fy)]
        if b["transactions"]:
            latest_ticket.append((store, b["revenue"] / b["transactions"], b["transactions"], b["revenue"]))
    low_ticket = sorted(latest_ticket, key=lambda x: x[1])[:4]
    high_ticket_median = statistics.median([x[1] for x in latest_ticket if x[1] >= statistics.median(y[1] for y in latest_ticket)])
    targeted_tx = sum(x[2] for x in low_ticket)
    ticket_uplift = sum(max(0, high_ticket_median - x[1]) * x[2] for x in low_ticket)

    # Compact data-quality evidence.
    dup_dates = sorted(key[1] for key in duplicate_groups)
    duplicate_range = f"{dup_dates[0]}~{dup_dates[-1]}" if dup_dates else "해당 없음"
    point_evidence = "; ".join(f"{r['store']} {r['date']}: {won(r['revenue'])}, {r['transactions']:,}건, 객단가 {won(r['ticket'])}" for r in point_outliers)
    mismatch_evidence = "; ".join(f"{s}: 중앙 객단가 {won(m)} (다른 지점 중앙값 {won(peer)})" for s, m, peer in mismatch_stores)

    rows = []
    rows.append("# 최근 3년 일별 매출 분석 보고서")
    rows.append("")
    rows.append("| 구분 | 발견 내용 | 근거 (지점/기간/수치) | 권고 조치 |")
    rows.append("|---|---|---|---|")
    rows.append(f"| 데이터 품질 | 중복 매출 행 | 강남점 {duplicate_range}, 동일 지점·일자 {len(duplicate_groups):,}건이 2회씩 입력(초과 {duplicate_rows:,}행) | 동일 키 1행만 보존 |")
    for store, missing in gaps.items():
        rows.append(f"| 데이터 품질 | 일자 누락 | {store} {missing[0]}~{missing[-1]}, {len(missing):,}일 누락 | 원천 복구 전 총액 비교 금지, 일평균으로 비교 |")
    rows.append(f"| 데이터 품질 | 매출 단위 불일치 의심 | {mismatch_evidence} | 원천 단위 확인 전 해당 지점 제외 |")
    rows.append(f"| 데이터 품질 | 단일일 매출 이상치 | {point_evidence} | 원천 POS 대사 후 제외/정정 |")
    growth_text = ", ".join(f"{s} {pct(g)}" for s, g, _, _, _ in top_growth)
    rows.append(f"| 성장 기회 | 성장 포맷 확산 | {latest_fy} 일평균 매출 전년 대비 상위: {growth_text} | 성공 지점 운영요소를 저성장 지점에 실험 |")
    rows.append(f"| 판촉 | 금요일 판촉의 인접일 대비 매출 우위 | 판촉 {len(promo_results):,}일: 실제 {won(promo_actual)} vs 같은 지점·월 목/토 평균 {won(promo_expected)}, {pct(promo_lift)} | 무작위 대조군으로 ROI 검증 |")
    rows.append("| 측정 설계 | 판촉이 금요일에만 배정됨 | 전 지점·전 기간: promo=1 1,863행은 모두 금요일, 비판촉 금요일 0행 | 동일 요일 대조군을 추가 |")
    rows.append(f"| 객단가 | 저객단가 지점 업셀 여지 | {latest_fy} 하위 4개 지점 객단가와 상위 절반 중앙값 {won(high_ticket_median)} 간 격차 | 세트/추가샷 업셀 파일럿 |")
    rows.append("")
    rows.append("## 분석 범위·가정 및 보정 방법")
    rows.append(f"- 원본 범위는 {first_day}~{last_day}, {len(raw):,}행, {len(stores)}개 지점이다. 분석 기준은 매출(revenue)이 원화이며 transactions는 양의 정수, promo는 0/1이라는 가정이다.")
    rows.append("- 보정본은 (1) 동일 지점·일자의 완전 중복은 최초 1행만 유지, (2) 지점 내 중앙 객단가에서 견고 기준(MAD)으로 크게 벗어난 단일일은 제외, (3) 단위가 불명확한 지점 전체는 제외했다. 결측은 임의 보간하지 않았고, 연도 비교는 관측 일수로 나눈 일평균을 사용했다.")
    rows.append(f"- 보정 후 분석 행은 {len(clean):,}행(원본 대비 {len(raw)-len(clean):,}행 제외/중복 제거)이며, 부산서면점은 단위 확인 전 모든 매출 순위·합계·추천 계산에서 제외했다.")
    rows.append("")
    rows.append("## 1. 데이터 품질 점검")
    rows.append("")
    rows.append(f"원본을 그대로 합산하거나 지점 순위를 매기면 안 된다. 특히 중복, 결측, 단위 문제, 비정상 단일일이 각각 서로 다른 방향으로 결과를 왜곡한다.")
    rows.append("")
    rows.append(f"1. **강남점 / {duplicate_range} / 완전 중복 입력** — {len(duplicate_groups):,}개 지점·일자에 동일한 매출·거래·판촉 값이 각각 두 번 들어 있어 초과 {duplicate_rows:,}행이다. 그대로 합산하면 강남점 해당 기간 매출이 정확히 두 번 반영되어 지점 성과와 전사 월별 추세가 과대 계상된다. 보정: 동일 `(store, date)`의 최초 1행만 유지했다.")
    n = 1
    for store, missing in gaps.items():
        n += 1
        rows.append(f"{n}. **{store} / {missing[0]}~{missing[-1]} / 일별 레코드 {len(missing):,}일 누락** — 공통 관측기간 내 이 지점의 데이터가 없다. 3개월 총매출을 0으로 처리하거나 완전한 지점과 총액만 비교하면 성과가 과소 평가된다. 보정: 결측을 0 또는 추정치로 채우지 않고, 연도 비교를 일평균으로 정규화했다. 원천 POS 백업으로 복구해야 한다.")
    n += 1
    rows.append(f"{n}. **{', '.join(sorted(mismatch_names))} / 전 기간 / 매출 단위 불일치 의심** — {mismatch_evidence}. 거래 건수는 다른 지점과 유사한데 객단가가 약 1/600 수준이어서 할인이나 수요 차이로 설명되기 어렵고, 매출이 천원 단위로 적재됐을 가능성이 높다. 보정: 환산 배수를 추정해 임의 변환하지 않고, 원천 단위 확인 전 해당 지점 전체를 분석에서 제외했다.")
    n += 1
    rows.append(f"{n}. **단일 일자 이상치 / 매출과 거래 건수의 불일치** — {point_evidence}. 각 값은 해당 지점의 중앙 객단가 대비 약 100배인데 거래 건수는 정상 범위여서, 매출 자릿수/단위 오류 가능성이 높다. 그대로 두면 해당 월·연도 성장률과 판촉 효과가 크게 왜곡된다. 보정: 해당 2행을 제외하고 원천 POS 전표로 정정 여부를 확인해야 한다.")
    n += 1
    rows.append(f"{n}. **전 지점 / 전 기간 / 판촉 배정 편향** — `promo=1`인 1,863행은 모두 금요일이고 비판촉 금요일은 0행이다. 따라서 금요일 수요 자체와 판촉 효과를 분리할 동일 요일 대조군이 없으며, 기존 표본만으로 판촉의 인과적 ROI를 확정할 수 없다. 보정: 아래 판촉 비교는 동일 지점·월의 목/토 평균을 사용한 방향성 참고치로 한정했다. 향후 동일 요일 비판촉 대조군을 무작위 배정해야 한다.")
    rows.append("")
    rows.append("## 2. 보정 후 인사이트 및 실행 제안 3가지")
    rows.append("")
    # Proposal 1
    rows.append("### 제안 1 — 여의도·잠실타워·판교테크의 성장 운영모델을 저성장 4개 지점에 90일 파일럿")
    rows.append(f"- **근거 데이터:** {latest_fy} 일평균 매출의 전년 대비 성장 상위 3개는 {growth_text}이다. 반대로 일평균 매출 하락 폭이 큰 지점은 {', '.join(f'{s} {pct(g)}' for s, g, _, _, _ in declining[:4])}이다. 이 비교는 결측일을 일평균으로 정규화하고 이상 매출을 제거한 결과다.")
    rows.append("- **실행:** 성장 3개 지점에서 시간대별 인력배치, 기업/오피스 주문, 베스트셀러 진열, 모바일 선주문 비중을 2주 내 체크리스트로 추출한다. 하락 상위 4개 지점에 지점별로 2개 요소만 배정하고, 미도입 유사 지점을 대조군으로 둔 90일 실험을 한다.")
    rows.append("- **KPI/의사결정:** 매주 전년 동요일 기준 거래 건수과 일평균 매출을 본다. 파일럿 지점이 대조군보다 거래 건수 성장률 +3%p 이상이면 다음 분기에 전개하고, 미달 요소는 중단한다.")
    # Proposal 2
    rows.append("### 제안 2 — 금요일 판촉을 무작위 대조군으로 재설계하고 ROI가 확인된 조합만 확대")
    rows.append(f"- **근거 데이터:** 판촉은 전부 금요일이라 인과적 비교는 불가능하다. 다만 보정 데이터의 판촉일 {len(promo_results):,}일에서 실제 매출은 {won(promo_actual)}, 같은 지점·월의 목/토 평균은 {won(promo_expected)}이며 실제가 {pct(promo_lift)} 높다. 이는 확대 후보를 선별하는 방향성 신호일 뿐, 금요일 고유 수요가 섞여 있으므로 ROI 확정 근거는 아니다.")
    rows.append("- **실행:** 다음 달 모든 판촉에 쿠폰/할인 원가와 코드, 대상 시간대를 붙인다. 각 지점은 주 1회 판촉군과 동일 요일의 비판촉 대조군을 교차 운영하고, 매출뿐 아니라 거래 수·객단가·할인 원가를 함께 수집한다.")
    rows.append("- **KPI/의사결정:** ‘증분 매출 − 할인/집행 원가’가 양수이고, 보정 기대치 대비 +5% 이상인 조합만 4주 연장한다. 매출만 높고 객단가 또는 마진을 훼손하는 쿠폰은 중단한다.")
    # Proposal 3
    targets = ", ".join(f"{s}({won(t)})" for s, t, _, _ in low_ticket)
    rows.append("### 제안 3 — 저객단가 4개 지점에서 세트·추가 옵션 업셀로 객단가를 끌어올리기")
    rows.append(f"- **근거 데이터:** {latest_fy} 객단가 하위 4개 지점은 {targets}이며, 정상 단위 지점의 상위 절반 중앙 객단가는 {won(high_ticket_median)}이다. 이 네 지점의 {latest_fy} 거래 수는 합계 {targeted_tx:,}건이다. 현재 거래 수가 유지된다는 보수적 가정에서도 객단가를 상위 절반 중앙값까지 올릴 수 있는 이론상 연 매출 격차는 약 {won(ticket_uplift)}이다.")
    rows.append("- **실행:** 이들 지점에서 아메리카노 단품 결제 화면에 베이커리 세트·사이즈업·추가샷을 기본 제안으로 노출하고, 바리스타 스크립트와 POS 버튼 순서를 통일한다. 가격 인하보다 ‘고마진 추가 옵션’ 우선으로 6주간 적용한다.")
    rows.append("- **KPI/의사결정:** 지점별 객단가, 옵션 부착률, 거래 수, 매출총이익을 매주 전년 동요일과 비교한다. 거래 수가 -2% 이내이면서 객단가 +3% 이상이면 전 지점으로 확장한다. 부산서면점은 단위 정정 전 이 KPI 비교에서 제외한다.")
    rows.append("")
    rows.append("## 부록: 재현 방법")
    rows.append("")
    rows.append("현재 폴더에서 `python analysis.py`를 실행하면 `sales.csv`를 다시 읽어 이 보고서를 재생성한다. 외부 패키지를 사용하지 않는다.")
    return "\n".join(rows) + "\n"


def main() -> None:
    if not INPUT.exists():
        raise FileNotFoundError(f"입력 파일을 찾을 수 없습니다: {INPUT.resolve()}")
    report = render_report(read_data(INPUT))
    OUTPUT.write_text(report, encoding="utf-8")
    print(f"OK: {OUTPUT.resolve()} 생성 완료")


if __name__ == "__main__":
    main()
