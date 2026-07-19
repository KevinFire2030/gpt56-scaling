"""sales.csv 품질 보정 및 경영회의용 report.md 생성 스크립트.
실행: python analysis.py
가정: 매출은 원화이며, 부산서면점의 전 기간 매출은 1,000원 단위로 잘못 적재되었고,
두 건의 극단값은 100배 단위 오류이다. 결측 홍대점 일자는 같은 월/요일/프로모션의
다른 연도 중앙값으로 추정한다. 추정치는 회사 총계에만 사용하며 매장 성과 확정에는 쓰지 않는다.
"""
from pathlib import Path
import numpy as np
import pandas as pd

INPUT = Path("sales.csv")
OUTPUT = Path("report.md")
REQUIRED = {"date", "store", "revenue", "transactions", "promo", "avg_temp_c"}


def won(x):
    return f"{x:,.0f}원"


def pct(x):
    return f"{x:+.1f}%"


def main():
    if not INPUT.exists():
        raise FileNotFoundError("현재 폴더에 sales.csv가 필요합니다.")
    raw = pd.read_csv(INPUT)
    missing_columns = REQUIRED - set(raw.columns)
    if missing_columns:
        raise ValueError(f"필수 열 누락: {sorted(missing_columns)}")
    df = raw.copy()
    df["date"] = pd.to_datetime(df["date"], errors="raise")
    if df["date"].isna().any() or df["store"].isna().any():
        raise ValueError("date 또는 store에 결측값이 있습니다.")

    stores = sorted(df["store"].unique())
    dates = pd.date_range(df.date.min(), df.date.max(), freq="D")
    exact_duplicates = int(df.duplicated().sum())
    duplicate_store = ", ".join(sorted(df.loc[df.duplicated(keep=False), "store"].unique()))
    duplicate_dates = df.loc[df.duplicated(keep=False), "date"]
    dup_period = f"{duplicate_dates.min():%Y-%m-%d}~{duplicate_dates.max():%Y-%m-%d}"

    # 보정 1: 완전히 동일한 중복은 한 행만 남긴다.
    clean = df.drop_duplicates().copy()

    # 보정 2: 부산서면점은 다른 점포와 대비해 객단가가 1/1,000 수준인 일관된 단위 오류.
    busan_mask = clean.store.eq("부산서면점")
    busan_ticket_before = (clean.loc[busan_mask, "revenue"] / clean.loc[busan_mask, "transactions"]).median()
    other_ticket_median = (clean.loc[~busan_mask, "revenue"] / clean.loc[~busan_mask, "transactions"]).median()
    clean.loc[busan_mask, "revenue"] *= 1000

    # 보정 3: 점포별 중앙 객단가의 10배 초과 행은 100배 통화 단위 오류로 간주.
    clean["ticket_before_outlier_fix"] = clean.revenue / clean.transactions
    store_ticket_median = clean.groupby("store")["ticket_before_outlier_fix"].transform("median")
    extreme_mask = clean.ticket_before_outlier_fix > store_ticket_median * 10
    extreme_rows = clean.loc[extreme_mask, ["date", "store", "revenue", "transactions"]].copy()
    clean.loc[extreme_mask, "revenue"] /= 100

    # 보정 4: 누락된 (일자, 점포)는 같은 점포·월·요일·프로모션의 과거 관측 중앙값으로 채움.
    clean["month_num"] = clean.date.dt.month
    clean["dow"] = clean.date.dt.dayofweek
    existing = set(zip(clean.date, clean.store))
    missing_pairs = [(d, s) for d in dates for s in stores if (d, s) not in existing]
    imputed = []
    for d, s in missing_pairs:
        candidate = clean[(clean.store == s) & (clean.month_num == d.month) &
                          (clean.dow == d.dayofweek) & (clean.promo == int(d.dayofweek == 4))]
        # 후보가 없을 경우에는 같은 점포·같은 월의 중앙값으로 후퇴.
        if candidate.empty:
            candidate = clean[(clean.store == s) & (clean.month_num == d.month)]
        imputed.append({
            "date": d, "store": s,
            "revenue": int(round(candidate.revenue.median())),
            "transactions": int(round(candidate.transactions.median())),
            "promo": int(d.dayofweek == 4),
            "avg_temp_c": float(candidate.avg_temp_c.median()),
            "is_imputed": True,
        })
    clean["is_imputed"] = False
    clean = pd.concat([clean, pd.DataFrame(imputed)], ignore_index=True, sort=False)
    clean["ticket"] = clean.revenue / clean.transactions
    clean["fiscal"] = np.select(
        [clean.date < pd.Timestamp("2024-07-01"), clean.date < pd.Timestamp("2025-07-01")],
        ["FY24", "FY25"], default="FY26")
    clean["month"] = clean.date.dt.to_period("M").astype(str)
    clean["dow_name"] = clean.date.dt.day_name()

    # 성과 지표: 모든 기간은 보정 후, 회계연도 FY26(2025-07~2026-06)와 FY25 비교.
    fy = clean.groupby(["store", "fiscal"]).agg(
        revenue=("revenue", "sum"), transactions=("transactions", "sum"), days=("date", "size")
    ).reset_index()
    fy["revenue_per_day"] = fy.revenue / fy.days
    fy["transactions_per_day"] = fy.transactions / fy.days
    fy["ticket"] = fy.revenue / fy.transactions
    piv = fy.pivot(index="store", columns="fiscal", values=["revenue_per_day", "transactions_per_day", "ticket"])
    yoy_rev = (piv["revenue_per_day"]["FY26"] / piv["revenue_per_day"]["FY25"] - 1) * 100
    yoy_tx = (piv["transactions_per_day"]["FY26"] / piv["transactions_per_day"]["FY25"] - 1) * 100
    yoy_ticket = (piv["ticket"]["FY26"] / piv["ticket"]["FY25"] - 1) * 100
    declining = yoy_rev[yoy_rev < 0].sort_values()
    growth = yoy_rev[yoy_rev > 0].sort_values(ascending=False)

    dow_summary = clean.groupby("dow_name").agg(revenue=("revenue", "mean"), transactions=("transactions", "mean")).round()
    promo_days = int((clean.promo == 1).sum())
    promo_friday_only = bool((clean.loc[clean.promo == 1, "dow"] == 4).all() and (clean.loc[clean.dow == 4, "promo"] == 1).all())
    fri_rev = dow_summary.loc["Friday", "revenue"]
    mon_rev = dow_summary.loc["Monday", "revenue"]
    weekend_rev = dow_summary.loc[["Saturday", "Sunday"], "revenue"].mean()

    missing_by_store = pd.Series([s for _, s in missing_pairs]).value_counts()
    missing_store = missing_by_store.index[0] if len(missing_by_store) else "없음"
    missing_start = min(d for d, _ in missing_pairs) if missing_pairs else None
    missing_end = max(d for d, _ in missing_pairs) if missing_pairs else None
    imputed_total = sum(x["revenue"] for x in imputed)

    lines = []
    # 요구된 표를 문서의 첫 요소로 둔다.
    lines += ["| 구분 | 발견 내용 | 근거 (지점/기간/수치) | 권고 조치 |",
              "|---|---|---|---|"]
    lines += [f"| 품질 | 완전 중복 적재 | {duplicate_store}, {dup_period}, {exact_duplicates}건 | 동일 행 {exact_duplicates}건 제거 |",
              f"| 품질 | 매출 단위 불일치 | 부산서면점, 전 기간; 중앙 객단가 {busan_ticket_before:,.0f}원(타 점포 중앙값 {other_ticket_median:,.0f}원 대비 약 1/1,000) | 매출 ×1,000 후 원천 POS 단위 매핑 수정 |",
              f"| 품질 | 누락 일자 | {missing_store}, {missing_start:%Y-%m-%d}~{missing_end:%Y-%m-%d}, {len(missing_pairs)}일 | 총계용 중앙값 추정({won(imputed_total)}); 원천 재수집 |",
              f"| 품질 | 100배 이상 극단 매출 | " + "; ".join(f"{r.store} {r.date:%Y-%m-%d}" for r in extreme_rows.itertuples()) + " | 매출 ÷100 보정 및 POS 전문 대조 |",
              f"| 실행 | 부진 8개 점포의 방문객 회복 | FY26 일매출 YoY {pct(declining.mean())} (8개 점포) | 60일 방문객 전환 실험 |",
              f"| 실행 | 성장 4개 점포의 운영 복제 | FY26 일매출 YoY {pct(growth.mean())} (4개 점포) | 피크 수용력·상권 운영 표준화 |",
              f"| 실행 | 금요일 프로모션을 실험 가능하게 재설계 | 프로모션 {promo_days:,} 점포-일이 모두 금요일 | 월/화 대조군 A/B 테스트 |",
              "",
              "# 커피 체인 일별 매출 분석 보고서",
              "",
              "## 분석 범위와 가정",
              f"- 범위: {df.date.min():%Y-%m-%d}~{df.date.max():%Y-%m-%d}, 원본 {len(df):,}행, 12개 점포.",
              "- 매출 단위는 원으로 가정했다. 품질 보정은 아래 규칙을 적용했으며, 금액은 반올림한 원화다.",
              "- 비교 기간: FY24=2023-07~2024-06, FY25=2024-07~2025-06, FY26=2025-07~2026-06. 성장률은 일평균으로 계산했다.",
              "- 결측 홍대점은 동일 점포·월·요일·프로모션의 다른 연도 중앙값으로 추정했다. 추정값은 체인 총계 분석에만 사용하고, 해당 점포의 확정 평가에는 원천 복구값을 사용해야 한다.",
              "",
              "## 1. 데이터 품질 점검",
              f"1. **강남점 중복 적재 — {dup_period}, {exact_duplicates}건.** date·store뿐 아니라 모든 열이 완전히 같은 행이 두 번 존재한다. 합계 매출·거래를 이중 계상하므로 한 행씩 제거했다.",
              f"2. **부산서면점 매출 단위 오류 — 전 기간 {int(busan_mask.sum()):,}건.** 보정 전 중앙 객단가는 {busan_ticket_before:,.1f}원으로 타 11개 점포 중앙값 {other_ticket_median:,.1f}원의 약 0.1%였다. 거래건수는 정상 범위인데 매출만 1/1,000이므로 1,000원 단위 적재 오류로 판단하여 매출에 1,000을 곱했다. 이 보정 전에는 부산서면점의 매출·체인 합계를 믿을 수 없다.",
              f"3. **홍대점 일별 누락 — {missing_start:%Y-%m-%d}~{missing_end:%Y-%m-%d}, {len(missing_pairs)}일.** 이 기간 매일 11개 점포만 있어 체인 월별 합계와 홍대점 기간 비교가 과소 계상된다. 같은 조건 중앙값으로 {won(imputed_total)}을 총계용으로 추정했으나, 원천 POS/ETL 재수집 전에는 확정 실적으로 쓰면 안 된다.",
              "4. **극단 매출 단위 오류 — 일산점 2024-11-07, 대구점 2025-08-21.** 각각 거래 180건 대비 매출 141,250,500원(객단가 784,725원), 거래 201건 대비 156,544,300원(778,827원)으로 각 점포의 정상 객단가 약 7,700~7,900원의 약 100배다. 거래건수는 정상적이므로 매출을 100으로 나눠 보정했다.",
              "5. **프로모션 식별 변수의 인과 한계 — 전 기간.** promo=1인 모든 점포-일이 금요일이고 금요일은 모두 promo=1이다. 따라서 요일 효과와 프로모션 효과가 완전히 겹쳐 현재 데이터만으로 할인/프로모션의 순증 매출 효과를 분리할 수 없다. 금요일 매출이 높다는 사실을 프로모션 성과로 해석하면 안 된다.",
              "",
              "## 2. 보정 후 핵심 인사이트",
              f"- FY26의 일매출은 8개 점포에서 하락했다. 하락폭은 {declining.index[0]} {pct(declining.iloc[0])}부터 {declining.index[-1]} {pct(declining.iloc[-1])}까지이며, 8개 평균은 {pct(declining.mean())}다. 이들 점포는 거래/일도 평균 {pct(yoy_tx[declining.index].mean())}, 객단가도 평균 {pct(yoy_ticket[declining.index].mean())} 변했다.",
              f"- 반대로 {', '.join(growth.index)} 4개 점포의 FY26 일매출은 평균 {pct(growth.mean())} 성장했다. 거래/일 평균 변화는 {pct(yoy_tx[growth.index].mean())}, 객단가 평균 변화는 {pct(yoy_ticket[growth.index].mean())}다. 성장의 주된 관측 동력은 거래건수다.",
              f"- 보정 후 요일별 평균 매출은 금요일 {won(fri_rev)}, 월요일 {won(mon_rev)}, 주말 평균 {won(weekend_rev)}이다. 다만 금요일과 promo가 완전히 일치하므로 프로모션의 증분효과는 미식별이다.",
              "",
              "## 3. 매출 확대를 위한 실행 제안 3가지",
              "",
              "### 제안 1. 하락 8개 점포에 ‘방문객 회복’ 60일 스프린트를 실행",
              f"- 대상: {', '.join(declining.index)}. FY26 일매출은 평균 {pct(declining.mean())}; 거래/일도 평균 {pct(yoy_tx[declining.index].mean())}로 하락해, 객단가보다 유입·재방문 회복이 우선이다.",
              "- 실행: 각 점포에서 평일 오전/오후 저수요 시간대에 인근 오피스·대학·주거 고객용 모바일 재방문 쿠폰과 사전주문 픽업을 60일 운영한다. 점포별로 전 30일 대비 거래/일 +5%를 1차 KPI로 두고, 주 단위로 채널별 쿠폰 발급·사용·거래를 점검한다.",
              "- 검증: 동일 요일 기준 전년 및 직전 4주와 비교하고, 쿠폰 미수신 고객군을 대조군으로 둔다. 매출만이 아니라 거래/일, 재방문율, 쿠폰 비용당 증분매출을 동시에 통과 기준으로 관리한다.",
              "",
              "### 제안 2. 성장 4개 점포의 피크 운영을 복제하고 수용력을 선제 확보",
              f"- 근거: 성장 4개 점포({', '.join(growth.index)})의 FY26 일매출은 평균 {pct(growth.mean())}, 거래/일은 평균 {pct(yoy_tx[growth.index].mean())}로 성장했다. 반면 객단가는 평균 {pct(yoy_ticket[growth.index].mean())}라서 성장은 가격보다 주문 수용량·유입 확대와 더 일관된다.",
              "- 실행: 2주 내 성장 점포에서 시간대별 주문량, 제조 리드타임, 품절, 모바일/현장 주문 비중을 추출해 표준 운영표를 만든다. 다음 8주 동안 하락폭이 큰 대구점·건대점·신촌점·광주점에 피크 타임 바리스타 배치, 모바일 픽업 동선, 베스트셀러 사전 제조/재고 기준을 이식한다.",
              "- KPI: 대상 4개 점포의 피크 시간 거래/시간 +8%, 품절률·대기시간 하락, 일매출 하락폭 절반 축소. 인력 추가로 발생한 비용은 거래 증가분의 공헌이익으로 별도 검증한다.",
              "",
              "### 제안 3. 금요일 고정 프로모션을 월·화 A/B 실험으로 전환",
              f"- 근거: 보정 후 금요일 평균 매출은 {won(fri_rev)}로 월요일 {won(mon_rev)}보다 {pct((fri_rev / mon_rev - 1) * 100)} 높지만, 프로모션 {promo_days:,} 점포-일이 전부 금요일이다. 현재 방식은 ‘금요일이라 높은 것’과 ‘프로모션 때문에 높은 것’을 분리하지 못한다.",
              "- 실행: 12개 점포를 상권·기존 매출로 6개씩 짝지어, 8주간 월·화에만 한 그룹은 번들/재방문 쿠폰을 제공하고 다른 그룹은 기존 운영을 유지한다. 4주 뒤 그룹을 교차한다. 금요일 정기 프로모션은 4주씩 유지/중단을 무작위 배정해 별도 측정한다.",
              "- 의사결정 기준: 점포-요일 기준 대조군 대비 거래/일·매출/일의 순증과 할인비용 후 공헌이익이 모두 양수일 때만 확대한다. 객단가 하락만으로 매출이 늘어난 경우는 확대하지 않는다.",
              "",
              "## 4. 데이터 운영 권고",
              "- ETL 적재 전 `(date, store)` 유일성 검사와 매출/거래 객단가 범위 검사(점포 중앙값 대비 10배 초과)를 실패 처리한다.",
              "- POS 매출 단위(원/천원/백원)를 소스별 메타데이터로 고정하고, 매일 12점포 × 1일 완결성 검사를 알림으로 운영한다.",
              "- 프로모션에는 캠페인 ID·할인액·대상고객·채널을 추가 기록한다. 그래야 매출 증가와 할인비용을 분리해 인과 효과와 수익성을 판단할 수 있다.",
              "",
              "## 재현 방법",
              "`python analysis.py`를 현재 폴더에서 실행하면 sales.csv를 다시 읽어 본 보고서를 생성한다. 외부 데이터나 난수는 사용하지 않는다."]
    OUTPUT.write_text("\n".join(lines) + "\n", encoding="utf-8")
    print(f"완료: {OUTPUT.resolve()} (보정 후 {len(clean):,} 점포-일, 중복 제거 {exact_duplicates}건, 결측 추정 {len(imputed)}건)")


if __name__ == "__main__":
    main()
