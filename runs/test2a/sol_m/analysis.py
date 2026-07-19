from __future__ import annotations

from pathlib import Path
import numpy as np
import pandas as pd

INPUT = Path("sales.csv")
REPORT = Path("report.md")
EXPECTED_COLUMNS = {
    "date", "store", "revenue", "transactions", "promo", "avg_temp_c"
}
GROWTH_STORES = ["부산서면점", "여의도점", "잠실타워점", "판교테크점"]
DECLINING_STORES = ["강남점", "건대점", "광주점", "대구점", "수원점", "신촌점", "일산점"]


def won(value: float) -> str:
    return f"{value / 100_000_000:,.2f}억원"


def pct(value: float) -> str:
    return f"{value * 100:,.1f}%"


def interpolate_same_weekday(frame: pd.DataFrame, store: str, column: str) -> pd.Series:
    """Linear interpolation using observations from the same weekday."""
    result = frame.loc[frame["store"].eq(store), ["date", column]].copy()
    result["dow"] = result["date"].dt.dayofweek
    result = result.set_index("date")[column]
    store_rows = frame["store"].eq(store)
    for dow in range(7):
        dates = frame.loc[store_rows & frame["date"].dt.dayofweek.eq(dow), "date"]
        values = result.reindex(dates)
        result.loc[dates] = values.interpolate(method="time", limit_direction="both")
    return result


def load_and_validate() -> pd.DataFrame:
    if not INPUT.exists():
        raise FileNotFoundError("sales.csv가 현재 폴더에 없습니다.")
    raw = pd.read_csv(INPUT)
    missing_columns = EXPECTED_COLUMNS.difference(raw.columns)
    if missing_columns:
        raise ValueError(f"필수 열 누락: {sorted(missing_columns)}")
    raw["date"] = pd.to_datetime(raw["date"], errors="raise")
    for column in ["revenue", "transactions", "promo", "avg_temp_c"]:
        raw[column] = pd.to_numeric(raw[column], errors="raise")
    return raw


def clean_data(raw: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    diagnostics: dict[str, object] = {}

    duplicate_extra = raw.duplicated(["date", "store"], keep="first")
    duplicate_rows = raw.loc[duplicate_extra]
    diagnostics["duplicate_count"] = int(duplicate_extra.sum())
    diagnostics["duplicate_revenue"] = float(duplicate_rows["revenue"].sum())
    diagnostics["duplicate_transactions"] = int(duplicate_rows["transactions"].sum())

    clean = raw.drop_duplicates(["date", "store"], keep="first").copy()

    # 부산서면점 revenue is consistently in thousand-won while all other revenue is won.
    busan = clean["store"].eq("부산서면점")
    diagnostics["busan_raw_ticket"] = float(
        clean.loc[busan, "revenue"].sum() / clean.loc[busan, "transactions"].sum()
    )
    clean.loc[busan, "revenue"] = clean.loc[busan, "revenue"] * 1000

    # Two isolated values are approximately 100x their local/store ticket level.
    spike_rules = [("일산점", "2024-11-07"), ("대구점", "2025-08-21")]
    spike_details = []
    for store, date_text in spike_rules:
        date = pd.Timestamp(date_text)
        hit = clean["store"].eq(store) & clean["date"].eq(date)
        if hit.sum() != 1:
            raise ValueError(f"예상 이상치가 정확히 1건이 아님: {store} {date_text}")
        raw_value = float(clean.loc[hit, "revenue"].iloc[0])
        nearby = (
            clean["store"].eq(store)
            & clean["date"].between(date - pd.Timedelta(days=14), date + pd.Timedelta(days=14))
            & ~clean["date"].eq(date)
        )
        local_median = float(clean.loc[nearby, "revenue"].median())
        spike_details.append((store, date_text, raw_value, local_median, raw_value / local_median))
        clean.loc[hit, "revenue"] = clean.loc[hit, "revenue"] / 100
    diagnostics["spikes"] = spike_details

    clean["revenue"] = clean["revenue"].round().astype("int64")
    clean["transactions"] = clean["transactions"].round().astype("int64")

    stores = sorted(clean["store"].unique())
    all_dates = pd.date_range(clean["date"].min(), clean["date"].max(), freq="D")
    complete_index = pd.MultiIndex.from_product([all_dates, stores], names=["date", "store"])
    indexed = clean.set_index(["date", "store"])
    missing_keys = complete_index.difference(indexed.index)
    diagnostics["missing_count"] = len(missing_keys)
    diagnostics["missing_stores"] = sorted(set(missing_keys.get_level_values("store")))
    diagnostics["missing_min"] = missing_keys.get_level_values("date").min()
    diagnostics["missing_max"] = missing_keys.get_level_values("date").max()

    # Reindex and impute the one missing block. Revenue/transactions use same-weekday
    # linear interpolation so weekend effects are not mixed with weekdays.
    complete = indexed.reindex(complete_index).reset_index()
    for column in ["revenue", "transactions"]:
        interpolated = interpolate_same_weekday(complete, "홍대점", column)
        target = complete["store"].eq("홍대점") & complete[column].isna()
        complete.loc[target, column] = complete.loc[target, "date"].map(interpolated)
    missing_temp = complete["avg_temp_c"].isna()
    date_temp = complete.groupby("date")["avg_temp_c"].median()
    complete.loc[missing_temp, "avg_temp_c"] = complete.loc[missing_temp, "date"].map(date_temp)
    missing_promo = complete["promo"].isna()
    complete.loc[missing_promo, "promo"] = complete.loc[missing_promo, "date"].dt.dayofweek.eq(4).astype(int)
    complete["revenue"] = complete["revenue"].round().astype("int64")
    complete["transactions"] = complete["transactions"].round().astype("int64")
    complete["promo"] = complete["promo"].astype("int64")
    complete["imputed"] = complete.set_index(["date", "store"]).index.isin(missing_keys)

    diagnostics["promo_friday_only"] = bool(
        raw.loc[raw["promo"].eq(1), "date"].dt.dayofweek.eq(4).all()
        and raw.loc[raw["date"].dt.dayofweek.eq(4), "promo"].eq(1).all()
    )
    diagnostics["promo_count"] = int(raw["promo"].eq(1).sum())
    diagnostics["negative_count"] = int(
        (raw[["revenue", "transactions"]] < 0).any(axis=1).sum()
    )
    diagnostics["raw_rows"] = len(raw)
    diagnostics["clean_rows"] = len(complete)
    diagnostics["nulls_after"] = int(complete.isna().sum().sum())
    return complete, diagnostics


def calculate_insights(clean: pd.DataFrame) -> dict:
    # Use 12-month operating years. Longitudinal recommendations exclude Hongdae
    # because its Y2 contains imputation, leaving 11 directly comparable stores.
    clean = clean.copy()
    clean["year"] = np.select(
        [clean["date"].le("2024-06-30"), clean["date"].le("2025-06-30")],
        ["Y1", "Y2"],
        default="Y3",
    )
    clean["dow"] = clean["date"].dt.dayofweek
    observed = clean.loc[~clean["imputed"]].copy()
    annual = observed.groupby(["store", "year"], as_index=False).agg(
        revenue=("revenue", "sum"), transactions=("transactions", "sum"), days=("date", "size")
    )
    annual["ticket"] = annual["revenue"] / annual["transactions"]
    wide = annual.pivot(index="store", columns="year", values=["revenue", "transactions", "ticket", "days"])
    comparable = [s for s in wide.index if wide.loc[s, ("days", "Y2")] == 365]

    def group_change(stores: list[str]) -> tuple[float, float, float, float, float]:
        y1_rev = float(wide.loc[stores, ("revenue", "Y1")].sum())
        y3_rev = float(wide.loc[stores, ("revenue", "Y3")].sum())
        y1_tx = float(wide.loc[stores, ("transactions", "Y1")].sum())
        y3_tx = float(wide.loc[stores, ("transactions", "Y3")].sum())
        return y1_rev, y3_rev, y3_rev / y1_rev - 1, y3_tx / y1_tx - 1, y3_rev - y1_rev

    growth = group_change(GROWTH_STORES)
    declining = group_change(DECLINING_STORES)
    complete_y3_revenue = float(wide.loc[comparable, ("revenue", "Y3")].sum())

    transaction_opportunity = float(
        (
            (wide.loc[DECLINING_STORES, ("transactions", "Y1")] - wide.loc[DECLINING_STORES, ("transactions", "Y3")])
            * wide.loc[DECLINING_STORES, ("ticket", "Y1")]
        ).sum()
    )
    ticket_opportunity = float(
        (
            (wide.loc[comparable, ("ticket", "Y1")] - wide.loc[comparable, ("ticket", "Y3")])
            * wide.loc[comparable, ("transactions", "Y3")]
        ).sum()
    )
    store_ticket_changes = (
        wide.loc[comparable, ("ticket", "Y3")] / wide.loc[comparable, ("ticket", "Y1")] - 1
    )

    # Normalize within store x operating-year x calendar-month to control mix/trend/season.
    observed["rev_norm"] = observed["revenue"] / observed.groupby(
        ["store", "year", observed["date"].dt.month]
    )["revenue"].transform("mean")
    weekday = observed.groupby("dow")["rev_norm"].mean()
    saturday_premium = float(weekday.loc[5] - 1)

    latest = observed[observed["year"].eq("Y3")]
    growth_saturday_revenue = float(
        latest.loc[latest["store"].isin(GROWTH_STORES) & latest["dow"].eq(5), "revenue"].sum()
    )

    return {
        "growth": growth,
        "declining": declining,
        "growth_share_y3": growth[1] / complete_y3_revenue,
        "transaction_opportunity": transaction_opportunity,
        "ticket_opportunity": ticket_opportunity,
        "median_ticket_change": float(store_ticket_changes.median()),
        "all_ticket_declined": bool((store_ticket_changes < 0).all()),
        "saturday_premium": saturday_premium,
        "growth_saturday_revenue": growth_saturday_revenue,
        "saturday_5pct_scenario": growth_saturday_revenue * 0.05,
        "comparable_store_count": len(comparable),
    }


def make_report(d: dict, i: dict) -> str:
    spike1, spike2 = d["spikes"]
    growth = i["growth"]
    decline = i["declining"]
    return f"""| 구분 | 발견 내용 | 근거 (지점/기간/수치) | 권고 조치 |
|---|---|---|---|
| 품질 | 동일 키 중복으로 매출·거래가 과대계상됨 | 강남점 / 2025-03-01~31 / 31행, {won(d['duplicate_revenue'])}, {d['duplicate_transactions']:,}건 중복 | 키당 1행만 유지하고 적재 단계에 유일성 제약 적용 |
| 품질 | 매출 단위 오류 | 부산서면점 / 전 기간 1,096일 / 원본 객단가 {d['busan_raw_ticket']:,.2f}원 | revenue를 1,000배 보정하고 원 단위로 통일 |
| 품질 | 장기 누락 구간 | 홍대점 / 2024-06-01~08-31 / {d['missing_count']}일 | 동일 요일 선형보간; 원천 POS 재수집 전까지 추정값 표시 |
| 품질 | 고립된 100배 매출 이상치 2건 | 일산점 2024-11-07 {spike1[2]:,.0f}원, 대구점 2025-08-21 {spike2[2]:,.0f}원 | 각 값을 100으로 나누고 승인 규칙 추가 |
| 품질 | 프로모션과 금요일이 완전 중첩되어 효과 식별 불가 | 전체 기간 / promo=1 {d['promo_count']:,}건이 모두 금요일이며 모든 금요일이 promo=1 | 금요일 무프로모션 대조군 또는 점포 무작위 홀드아웃 운영 |
| 인사이트 | 7개 감소 지점의 거래 회복 여지 | Y1→Y3 / 거래 {pct(decline[3])}, 매출 {pct(decline[2])}; 거래 회복 시나리오 {won(i['transaction_opportunity'])} | 지점별 CRM 재방문 캠페인으로 Y1 거래량 회복 |
| 인사이트 | 동일 지점 내 객단가가 전 지점 하락 | 비교 가능 11개점 / 객단가 중앙값 변화 {pct(i['median_ticket_change'])}; 회복 시나리오 {won(i['ticket_opportunity'])} | 세트·사이즈업·추가구매 제안으로 약 4% 회복 |
| 인사이트 | 성장 4개점과 토요일에 매출이 집중 | 성장 4개점 Y3 매출 비중 {pct(i['growth_share_y3'])}; 토요일 정규화 매출 +{pct(i['saturday_premium'])} | 토요일 피크 처리량을 성장점부터 5% 높이는 파일럿 |

# 커피 체인 3개년 매출 분석 보고서

## 결론

원본 데이터를 그대로 믿고 의사결정하면 안 된다. 중복, 단위 오류, 장기 누락, 100배 이상치가 합계와 지점 순위를 크게 왜곡한다. 아래 규칙으로 보정한 뒤에는 추세 분석에 사용할 수 있다. 다만 `promo` 효과는 금요일 효과와 분리할 수 없으므로 이 자료만으로 인과적 ROI를 주장하지 않는다.

## 분석 범위와 보정 가정

- 기간: 2023-07-01~2026-06-30(1,096일), 12개 지점.
- 12개월 운영연도: Y1=2023-07-01~2024-06-30, Y2=2024-07-01~2025-06-30, Y3=2025-07-01~2026-06-30.
- 중복은 `(date, store)`가 같은 두 번째 행을 제거했다.
- 부산서면점 매출은 원본 객단가가 13.44원으로 비현실적이고 전 기간에 일관되므로 천원 단위가 원 단위 열에 섞인 것으로 보고 1,000배 했다.
- 두 고립 이상치는 주변 4주 매출 중앙값의 각각 {spike1[4]:.1f}배, {spike2[4]:.1f}배이고 객단가도 해당 점포 정상 수준의 약 100배이므로 소수점/자리수 오류로 보고 100으로 나눴다.
- 홍대점 누락 92일은 같은 요일끼리 누락 전후 값을 선형보간했다. 보간 불확실성 때문에 전년 비교와 제안의 핵심 수치는 홍대점을 제외한 관측 완전 11개점으로 계산했다.
- 기온은 매출 보정에 사용하지 않았다. 누락행의 기온만 같은 날짜 타 지점 중앙값으로 채웠다.
- 모든 금액 기회는 과거 수준을 기계적으로 회복한다고 가정한 **연간 시나리오**이며 예측이나 인과효과가 아니다. 비용·마진 자료가 없어 매출 기준으로만 평가했다.

## 1. 데이터 품질 점검

1. **강남점 / 2025-03-01~2025-03-31 / 일별 행 31건이 정확히 두 번 들어가 있음 / 동일 `(date, store)`가 중복되어 원본 합계가 {won(d['duplicate_revenue'])}, {d['duplicate_transactions']:,}건 과대계상된다.** 두 번째 행을 제거했다. 앞으로 적재 DB에 `(date, store)` 유일성 제약과 중복 차단 로그를 둔다.

2. **부산서면점 / 2023-07-01~2026-06-30 전체 1,096일 / revenue 단위가 다른 지점과 1,000배 다름 / 원본 객단가가 {d['busan_raw_ticket']:,.2f}원으로 거래 {d['busan_raw_ticket']:,.2f}원당 1건이라는 불가능한 수준이다.** transactions 흐름은 정상이고 매출을 1,000배 하면 점포 객단가 범위와 정합하므로 천원→원 변환을 적용했다.

3. **홍대점 / 2024-06-01~2024-08-31 / 연속 {d['missing_count']}일이 없음 / 나머지 11개점과 다른 기간은 매일 존재하므로 휴점 표시가 아니라 추출 누락으로 보는 것이 합리적이다.** 동일 요일 선형보간값을 사용하되 `imputed=True`로 구분했다. 원천 POS를 복구하면 반드시 대체해야 한다.

4. **일산점·대구점 / 일산점 2024-11-07 {spike1[2]:,.0f}원, 대구점 2025-08-21 {spike2[2]:,.0f}원 / 주변 4주 중앙값 대비 {spike1[4]:.1f}배와 {spike2[4]:.1f}배 / 거래건수는 정상인데 객단가만 약 100배라 두 자리 입력 오류로 판단한다.** revenue를 각각 100으로 나눴다.

5. **전체 지점 / 전 기간 모든 금요일 / promo가 요일과 완전 공선성 / promo=1인 {d['promo_count']:,}행이 모두 금요일이고 모든 금요일 행이 promo=1이다.** 금요일 매출이 월~목보다 높아도 자연 요일 효과와 프로모션 효과를 분리할 수 없다. 프로모션 ROI 의사결정에는 금요일 무처치 지점 홀드아웃이 필요하다.

6. **전체 / 기본 형식 점검 / 날짜 파싱 실패와 필수값 결측은 없고, 음수 거래·매출은 {d['negative_count']}건이다.** 위 1~5를 처리한 완전 일자-지점 격자는 {d['clean_rows']:,}행이며 결측값은 {d['nulls_after']}개다.

## 2. 매출 증대를 위한 실행 제안 3가지

### 제안 1. 감소 7개점에서 거래건수 회복을 최우선 KPI로 둔다

- 대상: 강남·건대·광주·대구·수원·신촌·일산점.
- 근거: Y1→Y3 합산 매출은 {won(decline[0])}에서 {won(decline[1])}으로 {pct(decline[2])}, 거래는 {pct(decline[3])} 감소했다. 반면 성장 4개점은 거래가 {pct(growth[3])} 늘었다. 전사 평균만 보면 이 양극화가 가려진다.
- 실행: 최근 60일 미방문 고객 재방문 쿠폰, 점포 반경 제휴, 월~목 스탬프 보너스를 지점별 4주 처리군/대조군으로 운영한다. 할인액이 아니라 **증분 거래건수와 증분 공헌이익**으로 중단/확대한다.
- 목표·규모: 객단가를 Y1 수준으로 별도 회복한다는 조건에서 거래건수를 Y1로 되돌리는 연간 매출 시나리오는 **{won(i['transaction_opportunity'])}**이다. 이는 보장된 예측이 아니라 우선순위 산정용 상한 시나리오다.

### 제안 2. 전 지점에서 객단가 약 4% 회복 프로그램을 실행한다

- 근거: 관측 완전 11개점 모두 Y1 대비 Y3 객단가가 하락했고 지점별 변화 중앙값은 **{pct(i['median_ticket_change'])}**이다. 성장점도 거래 증가가 객단가 하락을 가리고 있다.
- 실행: (1) 음료+푸드 세트, (2) 사이즈업 기본 제안, (3) 결제 직전 저가 추가상품을 3개 군으로 나눠 6주 테스트한다. 지점·요일별 대조군을 남기고 거래당 매출과 공헌이익을 함께 본다.
- 목표·규모: 각 지점의 Y3 거래건수에서 자체 Y1 객단가만 회복할 경우 관측 완전 11개점의 연간 매출 시나리오는 **{won(i['ticket_opportunity'])}**이다. 믹스 변화 때문에 전사 가중 객단가만 보지 말고 동일 지점 지표를 사용한다.

### 제안 3. 성장 4개점의 토요일 피크 처리량에 자원을 집중한다

- 대상: 부산서면·여의도·잠실타워·판교테크점.
- 근거: 네 점포의 Y1→Y3 매출은 {pct(growth[2])}, 거래는 {pct(growth[3])} 증가했고, Y3 관측 완전 11개점 매출의 **{pct(i['growth_share_y3'])}**를 차지한다. 지점·운영연도·월 믹스를 통제한 토요일 매출은 일평균보다 **{pct(i['saturday_premium'])} 높아** 가장 강하다.
- 실행: 토요일 피크 시간대에 바리스타 교차배치, 사전 제조 가능한 품목 준비량, 모바일 픽업 슬롯과 장비 예방정비를 우선 배정한다. 4주간 주문 거절률·대기시간·시간당 거래를 측정하고, 대조 토요일 대비 처리량이 오른 점포만 상시화한다.
- 목표·규모: 성장 4개점의 Y3 토요일 매출은 {won(i['growth_saturday_revenue'])}이다. 처리량을 5% 높이고 수요가 이를 흡수한다는 단순 시나리오는 연 **{won(i['saturday_5pct_scenario'])}** 추가 매출이다. 대기시간 자료가 없으므로 먼저 파일럿으로 병목 존재를 확인한다.

## 지표 해석 시 주의사항

- `promo=1`은 금요일 표시와 사실상 동일하므로 현재 자료로 프로모션 인과효과를 계산하지 않았다.
- 매출 증대 시나리오끼리는 일부 겹칠 수 있어 단순 합산하지 않는다.
- 원가, 할인비, 인건비, 영업시간, 휴점, 대기시간이 없어 이익·수용능력은 별도 검증이 필요하다.
- 다음 적재부터 원 단위, 지점-일 유일키, 누락일 알림, 객단가 전일/4주 중앙값 대비 이상치 경보를 자동화한다.
"""


def main() -> None:
    raw = load_and_validate()
    clean, diagnostics = clean_data(raw)
    insights = calculate_insights(clean)
    report = make_report(diagnostics, insights)
    REPORT.write_text(report, encoding="utf-8")
    print(f"OK: {REPORT} 생성")
    print(f"원본 {diagnostics['raw_rows']:,}행 -> 완전 격자 {diagnostics['clean_rows']:,}행")
    print(f"중복 {diagnostics['duplicate_count']}행 제거, 누락 {diagnostics['missing_count']}행 보간")


if __name__ == "__main__":
    main()
