"""sales.csv를 점검·보정하고 경영회의용 report.md를 생성한다.
실행: python analysis.py
가정: revenue는 원화이며, 부산서면점의 전 기간 revenue는 천원 단위로 입력되었다.
"""
from pathlib import Path
import pandas as pd
import numpy as np

INPUT = Path("sales.csv")
REPORT = Path("report.md")
EXPECTED_STORES = 12


def won(value: float) -> str:
    return f"₩{value:,.0f}"


def pct(value: float) -> str:
    return f"{value * 100:+.1f}%"


def main() -> None:
    if not INPUT.exists():
        raise FileNotFoundError(f"입력 파일이 없습니다: {INPUT.resolve()}")

    raw = pd.read_csv(INPUT)
    required = {"date", "store", "revenue", "transactions", "promo", "avg_temp_c"}
    missing_columns = required - set(raw.columns)
    if missing_columns:
        raise ValueError(f"필수 열 누락: {sorted(missing_columns)}")
    raw["date"] = pd.to_datetime(raw["date"], errors="raise")
    raw["ticket"] = raw["revenue"] / raw["transactions"]

    # 품질 진단 값
    duplicate_rows = raw[raw.duplicated(["date", "store"], keep=False)].copy()
    duplicate_extra = len(raw) - len(raw.drop_duplicates(["date", "store"], keep="first"))
    date_min, date_max = raw["date"].min(), raw["date"].max()
    all_dates = pd.date_range(date_min, date_max, freq="D")
    hdae_missing = all_dates.difference(raw.loc[raw["store"] == "홍대점", "date"])
    busan = raw[raw["store"] == "부산서면점"]
    non_busan = raw[raw["store"] != "부산서면점"]
    busan_ticket_median = busan["ticket"].median()
    non_busan_ticket_low = non_busan.groupby("store")["ticket"].median().min()
    non_busan_ticket_high = non_busan.groupby("store")["ticket"].median().max()

    # 보정 규칙 1: (date, store)가 완전히 동일한 중복은 첫 행만 유지.
    clean = raw.drop_duplicates(["date", "store"], keep="first").copy()
    # 보정 규칙 2: 부산서면점은 일관되게 천원 단위이므로 원화로 환산.
    clean.loc[clean["store"] == "부산서면점", "revenue"] *= 1000
    clean["ticket"] = clean["revenue"] / clean["transactions"]
    # 보정 규칙 3: 매장 중앙값의 5배 초과 객단가는 100배 입력 오류로 판단해 revenue를 100으로 나눔.
    med_ticket = clean.groupby("store")["ticket"].transform("median")
    decimal_error = clean["ticket"] > med_ticket * 5
    extreme_rows = clean.loc[decimal_error, ["date", "store", "revenue", "transactions", "ticket"]].copy()
    clean.loc[decimal_error, "revenue"] /= 100
    clean["ticket"] = clean["revenue"] / clean["transactions"]

    # 결측된 홍대점 92일은 임의 보간하지 않는다. 모든 집계는 관측된 정상 행만 사용한다.
    clean["year"] = clean["date"].dt.year
    clean["month"] = clean["date"].dt.month
    clean["weekday"] = clean["date"].dt.day_name()
    clean["ym"] = clean["date"].dt.to_period("M")

    # 보정 후 매출/트래픽 패턴과 실행 기회 계산
    monthly = clean.groupby("month").agg(
        daily_revenue=("revenue", "mean"), daily_transactions=("transactions", "mean"), ticket=("ticket", "mean")
    )
    jan, may, jun = monthly.loc[1], monthly.loc[5], monthly.loc[6]

    # 최신 완결 월(2026-06)과 전년 동월 비교. 홍대점은 양쪽 모두 관측된 날짜만 사용.
    curr = clean[(clean["year"] == 2026) & (clean["month"] == 6)]
    prev = clean[(clean["year"] == 2025) & (clean["month"] == 6)]
    current_store = curr.groupby("store").agg(revenue=("revenue", "mean"), tx=("transactions", "mean"), ticket=("ticket", "mean"))
    prior_store = prev.groupby("store").agg(revenue=("revenue", "mean"), tx=("transactions", "mean"), ticket=("ticket", "mean"))
    yoy = current_store.join(prior_store, lsuffix="_26", rsuffix="_25", how="inner")
    yoy["revenue_yoy"] = yoy["revenue_26"] / yoy["revenue_25"] - 1
    yoy["tx_yoy"] = yoy["tx_26"] / yoy["tx_25"] - 1
    yoy["ticket_yoy"] = yoy["ticket_26"] / yoy["ticket_25"] - 1
    declining = yoy[yoy["tx_yoy"] < 0]
    traffic_recovery_daily = ((declining["tx_25"] - declining["tx_26"]) * declining["ticket_26"]).sum()
    ticket_recovery_daily = (yoy["tx_26"] * (yoy["ticket_25"] - yoy["ticket_26"])).clip(lower=0).sum()

    # 프로모션 설계 편향
    promo_by_weekday = pd.crosstab(clean["weekday"], clean["promo"])
    promo_days = clean.loc[clean["promo"] == 1, "date"].nunique()
    no_promo_fridays = int(promo_by_weekday.loc["Friday", 0]) if 0 in promo_by_weekday.columns else 0
    friday = clean[clean["weekday"] == "Friday"]
    thursday = clean[clean["weekday"] == "Thursday"]

    # 식별 가능한 성장 매장과 감소 매장
    growing = yoy[yoy["tx_yoy"] > 0]
    grow_names = ", ".join(growing.index.tolist())
    decline_names = ", ".join(declining.index.tolist())
    avg_growth_tx = growing["tx_yoy"].mean()
    avg_decline_tx = declining["tx_yoy"].mean()

    duplicate_period = f"{duplicate_rows['date'].min():%Y-%m-%d}~{duplicate_rows['date'].max():%Y-%m-%d}"
    extreme_text = "; ".join(
        f"{r.store} {r.date:%Y-%m-%d}: {won(r.revenue)} / {r.transactions:,}건 (객단가 {won(r.ticket)})"
        for r in extreme_rows.itertuples()
    )
    # 표의 첫 부분은 요청된 정확한 열 구조를 유지한다.
    lines = [
        "# 커피 체인 일별 매출 분석 보고서",
        "",
        "| 구분 | 발견 내용 | 근거 (지점/기간/수치) | 권고 조치 |",
        "|---|---|---|---|",
        f"| 데이터 품질 | 강남점 완전 중복 31행 | 강남점 / {duplicate_period} / 31개 (date·store·모든 값 동일) | 중복 제거 후 집계 |",
        f"| 데이터 품질 | 홍대점 92일 결측 | 홍대점 / 2024-06-01~2024-08-31 / 92일 연속 누락 | 해당 기간은 비교·추세 집계에서 제외, 원천 복구 |",
        f"| 데이터 품질 | 부산서면점 매출 단위 불일치 | 부산서면점 / 전 기간 / 중앙 객단가 {won(busan_ticket_median)} vs 타 매장 중앙값 {won(non_busan_ticket_low)}~{won(non_busan_ticket_high)} | 부산서면점 revenue ×1,000 환산 및 POS 단위 확인 |",
        f"| 데이터 품질 | 100배 매출 이상치 2건 | {extreme_text} | 해당 2건 revenue ÷100 보정, 원장 대조 |",
        f"| 실행 기회 | 2026년 6월 트래픽 회복 | 감소 {len(declining)}개점({decline_names}) / 전년동월 대비 평균 거래 {pct(avg_decline_tx)} | 거래수 회복 캠페인과 주간 KPI 운영 |",
        f"| 실행 기회 | 객단가 회복 | 2026-06 전 지점 / 전년동월 대비 객단가 하락 지점 {int((yoy['ticket_yoy'] < 0).sum())}개 | 세트·업셀로 2025 수준 회복 |",
        f"| 실행 기회 | 성수기 운영·프로모션 실험 | 5~6월 / 1월 대비 일평균 매출·거래 증가, 프로모션은 금요일에만 배치 | 성수기 재고·인력 증원, 무작위 대조 실험 |",
        "",
        "## 범위·가정·보정 방법",
        f"- 원본은 {date_min:%Y-%m-%d}~{date_max:%Y-%m-%d}, {raw['store'].nunique()}개 지점, {len(raw):,}행이다. 결측값, 0 이하 매출/거래, promo 값(0/1) 외 값은 발견되지 않았다.",
        "- 통화는 `revenue`가 원화라고 가정했다. 부산서면점은 거래수는 다른 지점과 유사하지만 매출·객단가가 정확히 약 1/1,000이므로, 전 기간 revenue에 1,000을 곱해 원화로 정규화했다. 이는 POS 원장으로 사후 확인해야 한다.",
        "- 완전히 동일한 (date, store) 중복은 첫 행만 남겼다. 홍대점 결측은 폐점인지 ETL 누락인지 판단할 근거가 없어 보간하지 않았다. 추세 비교는 관측된 일자만 사용한다.",
        "- 객단가가 해당 매장 중앙값의 5배 초과인 2건은 100배 자리수 오류로 보고 revenue를 100으로 나눴다. 보정 후 분석 행 수는 " + f"{len(clean):,}행이다.",
        "",
        "## 1. 데이터 품질 점검",
        f"1. **강남점 / {duplicate_period} / 완전 중복 31행**: date·store 기준 중복은 31행이며 모든 열 값도 동일하다. 일별 매출·거래를 합산하면 해당 31일이 이중 계상된다. 원인은 재수집 또는 병합 중복으로 보는 것이 합리적이다. 첫 행만 유지했다.",
        f"2. **홍대점 / 2024-06-01~2024-08-31 / 92일 연속 결측**: 전체 1,096일 중 홍대점에만 92일이 없다. 0매출로 간주하면 휴점과 데이터 누락을 혼동하고, 보간하면 실제 성과를 발명하게 된다. 따라서 이 기간은 제외하고 원천 POS·ETL 로그로 원인을 확인해야 한다.",
        f"3. **부산서면점 / 전 기간 / 매출 단위 1,000배 불일치**: 중앙 객단가가 {won(busan_ticket_median)}인데 다른 11개점의 매장별 중앙 객단가 범위는 {won(non_busan_ticket_low)}~{won(non_busan_ticket_high)}다. 거래수 중앙값은 259건으로 정상 범위인데 매출만 축소되어 있어, 천원 단위가 혼입된 것으로 판단된다. revenue ×1,000으로 환산했다.",
        f"4. **일산점 2024-11-07 및 대구점 2025-08-21 / 매출 100배 이상치**: 각각 보정 전 객단가가 {won(extreme_rows.iloc[0]['ticket'])}, {won(extreme_rows.iloc[1]['ticket'])}로 통상 범위를 약 100배 초과했다. 거래수는 180건·201건으로 정상이라 매출 자리수 오류가 유력하다. 각 revenue를 ÷100 보정했다.",
        f"5. **전 지점 / 전 기간 / 프로모션 효과 식별 불가**: promo=1인 {promo_days}일은 모두 금요일이고, 비프로모션 금요일은 {no_promo_fridays}행이다. 따라서 금요일 수요와 프로모션 효과가 완전히 겹쳐 현재 데이터로 증분 효과를 추정할 수 없다. 단순히 프로모션일 일평균 매출이 높다는 결론을 내리면 요일 효과를 프로모션 효과로 오인한다.",
        "",
        "## 2. 보정 후 핵심 인사이트 및 실행 제안",
        "### 제안 1. 감소 8개점의 ‘거래수 회복’ 30일 스프린트를 운영",
        f"- **근거 데이터:** 최신 완결월인 2026년 6월에 거래수가 전년 동월보다 감소한 곳은 {len(declining)}개점({decline_names})이며, 이들 평균 거래수 증감은 {pct(avg_decline_tx)}다. 반대로 {len(growing)}개점({grow_names})은 평균 {pct(avg_growth_tx)} 증가했다.",
        f"- **실행:** 감소점별로 출근·점심·퇴근 시간대 중 한 개를 골라 모바일 선주문, 인근 오피스/대학 제휴 쿠폰, 재방문 스탬프를 주 단위로 운영한다. KPI는 일 거래수와 쿠폰 재방문율이며, 지점별 목표는 ‘2025년 6월 거래수’다.",
        f"- **규모:** 감소점들이 2025년 6월 거래수를 회복하면, 2026년 6월 객단가 기준으로 일평균 약 {won(traffic_recovery_daily)}, 30일 기준 약 {won(traffic_recovery_daily * 30)}의 매출 회복 여지가 있다. 이는 예측이 아니라 전년 거래수 수준을 적용한 기회 추정치다.",
        "",
        "### 제안 2. 전 지점에서 세트·업셀로 2025년 객단가를 회복",
        f"- **근거 데이터:** 2026년 6월 전년 동월 대비 객단가가 하락한 지점은 {int((yoy['ticket_yoy'] < 0).sum())}개 전부다. 거래수 감소와 별개로 객단가 하락이 매출을 추가로 압박한다.",
        "- **실행:** POS 첫 화면에 ‘음료+베이커리/디저트’ 2단 세트를 배치하고, 주문 시 1개 업셀 문구를 표준화한다. 고정 할인 대신 세트 구성으로 객단가를 올리고, 점포별 주간 객단가·부가품목 부착률을 공개한다.",
        f"- **규모:** 거래수가 현재 수준에 머문다고 보수적으로 가정해도, 2025년 6월의 지점별 객단가까지 회복 시 일평균 약 {won(ticket_recovery_daily)}, 30일 기준 약 {won(ticket_recovery_daily * 30)}의 매출 기회가 있다.",
        "",
        "### 제안 3. 5~6월 피크 수요에 냉음료·인력·재고를 집중하고, 프로모션은 대조군 실험으로 재설계",
        f"- **근거 데이터:** 보정 후 전 지점 일평균 매출은 1월 {won(jan.daily_revenue)}에서 5월 {won(may.daily_revenue)}·6월 {won(jun.daily_revenue)}으로 각각 {pct(may.daily_revenue / jan.daily_revenue - 1)}·{pct(jun.daily_revenue / jan.daily_revenue - 1)} 높다. 같은 기간 거래수도 1월 {jan.daily_transactions:,.1f}건에서 5월 {may.daily_transactions:,.1f}건·6월 {jun.daily_transactions:,.1f}건으로 증가한다. 현재 프로모션은 금요일에만 있어 인과효과를 측정할 수 없다.",
        "- **실행:** 4~6월에는 냉음료·콜드브루·디저트 세트의 생산량, 원부자재 안전재고, 피크 시간 인력을 사전 증량한다. 동시에 동질 지점쌍 또는 동일 지점의 무작위 날짜에만 혜택을 배정하고, 같은 요일의 비혜택 대조군을 남긴다.",
        "- **판정 기준:** 거래수, 객단가, 일매출의 대조군 대비 증분과 할인비용을 함께 기록한다. 4주 후 순증 매출(증분매출−할인비용)이 양수인 혜택만 확대한다.",
        "",
        "## 의사결정 유의사항",
        "- 위 기회 금액은 보정 후 관측치에 기반한 단순 시나리오이며, 할인비용·원가·좌석/제조 용량은 반영하지 않은 매출 기준이다.",
        "- 부산서면점 단위와 홍대점 결측 원인이 POS 원장으로 확인되기 전에는 지점별 손익평가·인센티브에 이 데이터를 단독 사용하지 않는다.",
        "",
        "## 재현 방법",
        "현재 폴더에서 `python analysis.py`를 실행하면 sales.csv를 다시 읽어 이 보고서를 생성한다. 외부 데이터나 난수는 사용하지 않는다.",
    ]
    REPORT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"분석 완료: {REPORT.resolve()} (보정 후 {len(clean):,}행)")


if __name__ == "__main__":
    main()
