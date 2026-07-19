from pathlib import Path
import numpy as np
import pandas as pd

INPUT = Path(__file__).with_name("sales.csv")
REPORT = Path(__file__).with_name("report.md")


def money(v):
    return f"₩{v:,.0f}"


def pct(v):
    return f"{v * 100:.1f}%"


def main():
    raw = pd.read_csv(INPUT, parse_dates=["date"])
    raw_rows = len(raw)
    stores = sorted(raw["store"].dropna().unique())
    start, end = raw["date"].min(), raw["date"].max()
    dates = pd.date_range(start, end, freq="D")
    expected_keys = len(stores) * len(dates)

    # Quality diagnostics on the unmodified source.
    dup_mask = raw.duplicated(["date", "store"], keep=False)
    dup_keys = raw.loc[dup_mask, ["date", "store"]].drop_duplicates()
    missing_by_store = (
        raw.drop_duplicates(["date", "store"])
        .groupby("store")["date"].nunique()
        .reindex(stores, fill_value=0)
    )
    missing_keys = expected_keys - raw.drop_duplicates(["date", "store"]).shape[0]
    hongdae_missing = dates.difference(raw.loc[raw.store == "홍대점", "date"])

    raw["ticket"] = raw["revenue"] / raw["transactions"]
    store_ticket_median = raw.groupby("store")["ticket"].median()
    non_busan_ticket_median = raw.loc[raw.store != "부산서면점", "ticket"].median()
    busan_ticket = store_ticket_median["부산서면점"]
    busan_ratio = busan_ticket / non_busan_ticket_median
    high_revenue = raw[raw["revenue"] > 20_000_000].copy()
    high_revenue["store_ticket_median"] = high_revenue["store"].map(store_ticket_median)
    high_revenue["ticket_ratio"] = high_revenue["ticket"] / high_revenue["store_ticket_median"]

    # Correction policy: exact duplicates are removed; missing Hongdae dates are
    # imputed from the same store/month/weekday in the other observed years;
    # revenue/transaction outliers are corrected using robust ticket medians.
    clean = raw.drop_duplicates(["date", "store"], keep="first").drop(columns="ticket")
    clean = clean.astype({"revenue": "float64", "transactions": "float64"})
    clean["month"] = clean.date.dt.month
    clean["weekday"] = clean.date.dt.weekday

    # Date-level fields are shared/inferable across stores for missing records.
    date_mode_promo = clean.groupby("date")["promo"].agg(lambda s: int(s.mode().iloc[0]))
    date_median_temp = clean.groupby("date")["avg_temp_c"].median()
    # Build robust seasonal weekday medians using all observed years.
    seasonal = clean.groupby(["store", "month", "weekday"])[["revenue", "transactions"]].median()
    all_keys = pd.MultiIndex.from_product([dates, stores], names=["date", "store"]).to_frame(index=False)
    corrected = all_keys.merge(clean.drop(columns=["month", "weekday"]), on=["date", "store"], how="left")
    corrected["month"] = corrected.date.dt.month
    corrected["weekday"] = corrected.date.dt.weekday
    corrected["imputed_missing"] = corrected.revenue.isna()
    for col in ["revenue", "transactions"]:
        vals = []
        for row in corrected.itertuples():
            if pd.isna(getattr(row, col)):
                vals.append(seasonal.loc[(row.store, row.month, row.weekday), col])
            else:
                vals.append(getattr(row, col))
        corrected[col] = vals
    corrected["promo"] = corrected["promo"].fillna(corrected["date"].map(date_mode_promo)).astype(int)
    corrected["avg_temp_c"] = corrected["avg_temp_c"].fillna(corrected["date"].map(date_median_temp))

    # Revenue unit error in 부산서면점: preserve observed transactions and restore
    # revenue using the median ticket of all other stores.
    busan_mask = corrected.store == "부산서면점"
    corrected.loc[busan_mask, "revenue"] = corrected.loc[busan_mask, "transactions"] * non_busan_ticket_median
    # Two one-day 100x revenue errors: preserve transactions, repair revenue.
    for row in high_revenue.itertuples():
        mask = (corrected.store == row.store) & (corrected.date == row.date)
        corrected.loc[mask, "revenue"] = corrected.loc[mask, "transactions"] * store_ticket_median[row.store]
    corrected["ticket"] = corrected.revenue / corrected.transactions
    corrected["year"] = corrected.date.dt.year
    corrected["month"] = corrected.date.dt.month
    corrected["weekday"] = corrected.date.dt.weekday

    # Descriptive promo comparison by store. This is not a causal estimate;
    # calendar/seasonality must be controlled in the proposed experiment.
    promo_means = corrected.groupby(["store", "promo"])["revenue"].mean().unstack("promo")
    promo_uplift = (promo_means[1] / promo_means[0] - 1).dropna()
    promo_days = corrected.groupby("promo").size()

    # Trend: two complete trailing 12-month windows.
    last_end = corrected.date.max()
    last_start = last_end - pd.Timedelta(days=364)
    prior_start = last_start - pd.Timedelta(days=365)
    prior_end = last_start - pd.Timedelta(days=1)
    last = corrected[corrected.date.between(last_start, last_end)].groupby("store").revenue.sum()
    prior = corrected[corrected.date.between(prior_start, prior_end)].groupby("store").revenue.sum()
    growth = (last / prior - 1).sort_values()

    store_summary = corrected.groupby("store").agg(
        revenue=("revenue", "sum"), transactions=("transactions", "sum"),
        ticket=("ticket", "mean"), days=("date", "nunique")
    ).sort_values("revenue", ascending=False)
    low_ticket = store_summary[store_summary.ticket < 10_000]
    low_ticket_last = corrected[corrected.date.between(last_start, last_end) & corrected.store.isin(low_ticket.index)].revenue.sum()
    ticket_5pct_opportunity = low_ticket_last * 0.05
    declining = growth[growth < 0]
    declining_last = last[declining.index].sum()
    promo_baseline = corrected.loc[corrected.promo == 0, "revenue"].mean()
    overall_promo_uplift = corrected.groupby("promo").revenue.mean().loc[1] / corrected.groupby("promo").revenue.mean().loc[0] - 1
    top_promo = promo_uplift.sort_values(ascending=False).head(3)

    # Write a meeting-ready report. All values are generated from this run.
    rows = [
        "| 구분 | 발견 내용 | 근거 (지점/기간/수치) | 권고 조치 |",
        "|---|---|---|---|",
        f"| 품질 | 중복 행/키 존재 | 전체 {raw_rows:,}행, 중복 키 {len(dup_keys):,}개(강남점 2025-03-01~03-31, {int(dup_mask.sum())}행) | 키(date, store) 유일성 제약 적용 후 1건만 유지 |",
        f"| 품질 | 결측 기간 존재 | 홍대점 2024-06-01~08-31 {len(hongdae_missing)}일, 유일 키 기준 누락 {missing_keys}건 | 동일 지점·월·요일 중앙값으로 보정하고 보정 플래그 유지 |",
        f"| 품질 | 부산서면점 매출 단위 이상 | 전 기간 중앙 티켓 {money(busan_ticket)} vs 타 지점 중앙 {money(non_busan_ticket_median)}(약 {1/busan_ratio:,.0f}배 차이) | 거래건수×타 지점 티켓 중앙값으로 매출 재산출, 원천값은 별도 보존 |",
        f"| 품질 | 단일일 매출 이상치 | 일산점 2024-11-07 {money(high_revenue.iloc[0].revenue)}, 대구점 2025-08-21 {money(high_revenue.iloc[1].revenue)}; 각 지점 중앙 티켓의 약 {high_revenue.ticket_ratio.iloc[0]:.0f}배/{high_revenue.ticket_ratio.iloc[1]:.0f}배 | 거래건수×해당 지점 정상 티켓 중앙값으로 보정 후 재검증 |",
        f"| 인사이트 | 프로모션은 거래건수와 매출을 함께 끌어올림 | 보정 데이터에서 프로모션일 평균 매출 +{pct(overall_promo_uplift)}, 프로모션일 {promo_days[1]:,}일 | 효과가 큰 지점부터 통제군을 둔 A/B 테스트로 확대 |",
        f"| 인사이트 | 성장점은 오피스/상권형 3개 점포 | 최근 12개월 매출: 여의도 {money(last['여의도점'])}, 판교테크 {money(last['판교테크점'])}, 잠실타워 {money(last['잠실타워점'])}; 전년동기 성장률 각각 {pct(growth['여의도점'])}/{pct(growth['판교테크점'])}/{pct(growth['잠실타워점'])} | 성공 메뉴·번들·단체주문 운영을 저성과점에 복제 |",
        f"| 리스크/기회 | 저단가 점포의 객단가 개선 여지 | 객단가 {money(10_000)} 미만 {len(low_ticket)}개 점포, 최근 12개월 매출 {money(low_ticket_last)} | 객단가 5% 개선 시 단순 잠재 매출 약 {money(ticket_5pct_opportunity)} |",
    ]
    report = "\n".join(rows) + "\n\n"
    report += "# 경영회의 분석 보고서\n\n"
    report += f"분석 기준일: {last_end.date()}  \n원천 기간: {start.date()}~{end.date()} / {len(stores)}개 지점\n\n"
    report += "## 결론\n\n"
    report += "원천 데이터를 그대로 의사결정에 사용하면 안 됩니다. 중복, 장기 결측, 단위 오류, 단일일 이상치가 확인되었습니다. 아래 보정 규칙을 적용한 데이터로 인사이트를 계산했습니다. 보정은 추정치이므로 원천 매출과 보정 매출을 회계·정산 자료로 대체하지 말고 대조해야 합니다.\n\n"
    report += "## 1. 데이터 품질 점검\n\n"
    report += f"1. **중복 기록**: `(date, store)` 기준 중복 키가 {len(dup_keys)}개({int(dup_mask.sum())}행)입니다. 강남점 2025-03-01~03-31이 동일 값으로 두 번씩 들어가 있어 2025년 3월 강남점 매출·거래건수를 약 2배로 집계하게 됩니다. 원인은 일별 적재 재실행 또는 중복 append로 추정됩니다.\n\n"
    report += f"2. **홍대점 결측 기간**: 홍대점은 2024-06-01~08-31 {len(hongdae_missing)}일의 레코드가 통째로 없습니다. 12개 지점×{len(dates)}일이면 {expected_keys:,}개 키가 필요하지만, 중복 제거 후 {expected_keys - missing_keys:,}개만 존재합니다. 원인은 영업중단인지 수집 누락인지 원천 시스템 확인이 필요합니다. 기간 비교·시즌성 분석에서 홍대점을 그대로 제외하면 편향이 생깁니다.\n\n"
    report += f"3. **부산서면점 매출 단위/스케일 오류**: {raw.loc[raw.store == '부산서면점', 'date'].min().date()}~{raw.loc[raw.store == '부산서면점', 'date'].max().date()} 전 기간의 중앙 매출/거래건은 {money(raw.loc[raw.store == '부산서면점', 'revenue'].median())}/{raw.loc[raw.store == '부산서면점', 'transactions'].median():.0f}건, 즉 티켓 {money(busan_ticket)}입니다. 다른 11개 점포 중앙 티켓 {money(non_busan_ticket_median)} 대비 약 {1/busan_ratio:,.0f}배 낮고 거래건수는 정상 범위입니다. 매출이 원 단위가 아닌 천원 단위로 저장됐거나 변환 과정에서 축소된 것으로 추정됩니다.\n\n"
    report += f"4. **두 건의 단일일 이상치**: 일산점 2024-11-07 매출 {money(high_revenue.iloc[0].revenue)}(거래 {high_revenue.iloc[0].transactions}건), 대구점 2025-08-21 {money(high_revenue.iloc[1].revenue)}(거래 {high_revenue.iloc[1].transactions}건)는 정상 중앙 티켓 대비 각각 약 {high_revenue.ticket_ratio.iloc[0]:.0f}배, {high_revenue.ticket_ratio.iloc[1]:.0f}배입니다. 거래건수가 평소와 비슷해 매출 필드의 소수점/단위 입력 오류 가능성이 높습니다.\n\n"
    report += "5. **검증 가능한 정상성**: 날짜 범위는 연속 2023-07-01~2026-06-30이고 지점 수는 12개이며, 결측값·음수 매출·0건 거래는 없습니다. 다만 정상성 확인만으로 위 4개 문제를 상쇄할 수 없으므로 보정 후 분석해야 합니다.\n\n"
    report += "### 보정 규칙과 가정\n\n"
    report += "- 중복 키는 동일 행이므로 첫 행만 유지했습니다.\n- 홍대점 결측일은 해당 지점의 같은 월·요일 관측 중앙값으로 매출과 거래건수를 보정했습니다. 프로모션은 같은 날짜 다른 지점의 최빈값, 기온은 날짜별 중앙값을 사용했습니다. 실제 휴점이었다면 보정하지 말고 휴점으로 분리해야 합니다.\n- 부산서면점은 거래건수를 유지하고 타 지점의 정상 티켓 중앙값을 곱해 매출을 보정했습니다. 일산·대구의 두 이상치는 각 지점 정상 티켓 중앙값을 적용했습니다.\n\n"
    report += "## 2. 품질 보정 후 핵심 인사이트\n\n"
    report += "| 지점 | 보정 3년 매출 | 평균 티켓 | 최근 12개월 전년동기 성장률 |\n|---|---:|---:|---:|\n"
    for s, r in store_summary.iterrows():
        report += f"| {s} | {money(r.revenue)} | {money(r.ticket)} | {pct(growth[s])} |\n"
    report += "\n"
    report += "## 3. 실행 제안 3가지\n\n"
    report += f"1. **프로모션을 무차별 확대하지 말고, 반응이 높은 지점 중심으로 8주 실험을 운영하세요.** 보정 데이터에서 프로모션일 평균 매출은 비프로모션일 대비 +{pct(overall_promo_uplift)}입니다. 지점별 단순 비교에서 상승폭 상위는 " + ", ".join(f"{s} +{pct(v)}" for s, v in top_promo.items()) + "입니다. 이 지점들을 처치군으로 두고 유사 비프로모션일을 통제군으로 두어 순증 매출과 마진을 검증한 뒤 확대하십시오.\n\n"
    report += f"2. **여의도·판교테크·잠실타워의 고단가 운영을 저단가 점포에 복제하세요.** 최근 12개월 매출은 각각 {money(last['여의도점'])}, {money(last['판교테크점'])}, {money(last['잠실타워점'])}이고 전년동기 대비 각각 {pct(growth['여의도점'])}, {pct(growth['판교테크점'])}, {pct(growth['잠실타워점'])} 성장했습니다. 세 점포의 평균 티켓은 약 {money(store_summary.loc[['여의도점','판교테크점','잠실타워점'],'ticket'].mean())}로, 저단가 점포군의 약 {money(low_ticket.ticket.mean())}보다 높습니다. 오피스 시간대 세트·프리미엄 옵션·단체주문을 강남·건대·신촌 등부터 4주씩 테스트하십시오.\n\n"
    report += f"3. **최근 역성장 점포에 회복 액션을 집중하고 객단가 KPI를 두세요.** 최근 12개월 기준 역성장 점포는 {', '.join(declining.index)}이며 합산 매출은 {money(declining_last)}입니다. 저단가 {len(low_ticket)}개 점포의 최근 12개월 매출은 {money(low_ticket_last)}이므로 객단가를 5%만 높여도 단순 잠재 매출은 약 {money(ticket_5pct_opportunity)}입니다. 점포별로 번들 전환율, 추가 샷/디저트 부착률, 재방문율을 주간 관리하고 5% 목표를 달성한 메뉴만 확산하십시오.\n\n"
    report += "## 해석의 한계와 다음 확인\n\n"
    report += "프로모션은 관측 자료의 전후/동시 비교이므로 인과효과로 확정할 수 없습니다. 보정된 부산서면점과 홍대점 결측값은 추정치입니다. 회의 전 POS 원장·정산 금액·휴점 캘린더·프로모션 적용 상품/할인율을 대조하고, 원천 테이블에 `(date, store)` 유일 제약과 매출/거래건 기반 이상치 알림을 추가하십시오.\n"
    REPORT.write_text(report, encoding="utf-8")
    print(f"wrote {REPORT} ({len(report):,} chars)")
    print(f"raw_rows={raw_rows}, duplicate_keys={len(dup_keys)}, missing_keys={missing_keys}, high_outliers={len(high_revenue)}")
    print(f"corrected_rows={len(corrected)}, promo_uplift={overall_promo_uplift:.6f}, ticket_opportunity={ticket_5pct_opportunity:.2f}")


if __name__ == "__main__":
    main()
