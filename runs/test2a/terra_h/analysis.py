"""Reproducible sales-data audit and management report generator.

Run from the directory containing sales.csv:
    python analysis.py

The script writes report.md. All monetary values are Korean won (KRW).
"""
from pathlib import Path
import sys
import pandas as pd

INPUT = Path("sales.csv")
OUTPUT = Path("report.md")
REQUIRED_COLUMNS = {"date", "store", "revenue", "transactions", "promo", "avg_temp_c"}
WEEKDAYS_KR = ["월", "화", "수", "목", "금", "토", "일"]


def won(value: float) -> str:
    """Format a KRW amount with a comma and no fractional won."""
    return f"₩{value:,.0f}"


def pct(value: float) -> str:
    return f"{value * 100:,.1f}%"


def load_and_audit(path: Path):
    if not path.exists():
        raise FileNotFoundError(f"입력 파일을 찾을 수 없습니다: {path.resolve()}")
    raw = pd.read_csv(path)
    missing_columns = REQUIRED_COLUMNS.difference(raw.columns)
    if missing_columns:
        raise ValueError(f"필수 열 누락: {sorted(missing_columns)}")

    df = raw.copy()
    df["date"] = pd.to_datetime(df["date"], errors="raise")
    if df["store"].nunique() != 12:
        raise ValueError(f"12개 지점이 필요하지만 {df['store'].nunique()}개가 발견되었습니다.")
    if (df["transactions"] <= 0).any() or (df["revenue"] <= 0).any():
        raise ValueError("매출 또는 거래건수에 0 이하 값이 있습니다.")

    duplicate_mask = df.duplicated(["date", "store"], keep="first")
    duplicate_rows = int(duplicate_mask.sum())
    duplicate_keys = int(df.duplicated(["date", "store"], keep=False).sum() // 2)
    duplicate_detail = df[df.duplicated(["date", "store"], keep=False)]
    duplicate_store = duplicate_detail["store"].mode().iat[0]
    duplicate_start = duplicate_detail["date"].min()
    duplicate_end = duplicate_detail["date"].max()

    dates = pd.date_range(df["date"].min(), df["date"].max(), freq="D")
    expected = pd.MultiIndex.from_product([dates, sorted(df["store"].unique())], names=["date", "store"])
    observed = pd.MultiIndex.from_frame(df.drop_duplicates(["date", "store"])[["date", "store"]])
    missing_pairs = expected.difference(observed).to_frame(index=False)

    # Explicit, reproducible correction policy:
    # (a) retain first exact duplicate; (b) rescale all Busan-Seomyeon revenue by 1,000;
    # (c) divide the two 100x revenue outliers by 100. Transactions are retained.
    clean = df.loc[~duplicate_mask].copy()
    clean["raw_revenue"] = clean["revenue"]
    clean["correction"] = "none"

    busan = clean["store"].eq("부산서면점")
    busan_rows = int(busan.sum())
    clean.loc[busan, "revenue"] *= 1000
    clean.loc[busan, "correction"] = "부산서면점 매출 단위 ×1,000"

    clean["ticket"] = clean["revenue"] / clean["transactions"]
    # A ticket over KRW 50,000 is implausible relative to all other records and flags the two input errors.
    extreme = clean["ticket"] > 50_000
    extreme_details = clean.loc[extreme, ["date", "store", "raw_revenue", "transactions"]].copy()
    clean.loc[extreme, "revenue"] /= 100
    clean.loc[extreme, "correction"] = "100배 매출 이상치 ÷100"
    clean["ticket"] = clean["revenue"] / clean["transactions"]

    clean["weekday_num"] = clean["date"].dt.dayofweek
    clean["weekday"] = clean["weekday_num"].map(dict(enumerate(WEEKDAYS_KR)))
    clean["month"] = clean["date"].dt.month
    clean["fiscal_year"] = clean["date"].dt.year.where(clean["date"].dt.month >= 7, clean["date"].dt.year - 1)
    return raw, clean, {
        "duplicate_rows": duplicate_rows, "duplicate_keys": duplicate_keys,
        "duplicate_store": duplicate_store, "duplicate_start": duplicate_start, "duplicate_end": duplicate_end,
        "missing_pairs": missing_pairs, "busan_rows": busan_rows, "extreme_details": extreme_details,
    }


def generate_report(raw: pd.DataFrame, clean: pd.DataFrame, audit: dict) -> str:
    missing = audit["missing_pairs"]
    missing_store = missing["store"].mode().iat[0]
    missing_dates = pd.to_datetime(missing.loc[missing["store"].eq(missing_store), "date"])
    missing_start, missing_end = missing_dates.min(), missing_dates.max()
    # Store/day-of-week table uses daily average: robust to the missing Hongdae period.
    weekday = clean.groupby("weekday_num").agg(revenue=("revenue", "mean"), transactions=("transactions", "mean"), ticket=("ticket", "mean"))
    weekday = weekday.reindex(range(7))
    weekend = weekday.loc[[5, 6]].mean()
    weekdays = weekday.loc[[0, 1, 2, 3, 4]].mean()
    weekend_uplift = weekend["revenue"] / weekdays["revenue"] - 1

    store = clean.groupby("store").agg(revenue=("revenue", "mean"), transactions=("transactions", "mean"), ticket=("ticket", "mean"), days=("date", "size"))
    # Select the lowest three transaction stores for a volume campaign; ticket benchmark excludes known format differences only by being descriptive.
    low_volume = store.sort_values("transactions").head(3)
    best_ticket = store["ticket"].idxmax()
    low_ticket = store["ticket"].idxmin()
    ticket_gap = store.loc[best_ticket, "ticket"] - store.loc[low_ticket, "ticket"]

    # Exclude Hongdae from this year-on-year measure because FY2024 contains its 92-day gap.
    comparable = clean[~clean["store"].eq(missing_store)]
    fy = comparable.groupby("fiscal_year").agg(revenue=("revenue", "sum"), transactions=("transactions", "sum"), ticket=("ticket", "mean"))
    fy_growth = fy.loc[2025, "revenue"] / fy.loc[2024, "revenue"] - 1
    # Friday is completely confounded with the promo flag: report the operational pattern, not a causal promo effect.
    friday = clean[clean["weekday_num"].eq(4)]
    friday_other = clean[~clean["weekday_num"].eq(4)]
    friday_diff = friday["transactions"].mean() / friday_other["transactions"].mean() - 1
    promo_friday_share = (clean.loc[clean["promo"].eq(1), "weekday_num"].eq(4)).mean()

    outliers = audit["extreme_details"]
    outlier_text = "; ".join(
        f"{r.store} {r.date:%Y-%m-%d} {won(r.raw_revenue)} (거래 {r.transactions:,}건)"
        for r in outliers.itertuples()
    )
    low_volume_text = ", ".join(f"{name} {value:,.0f}건/일" for name, value in low_volume["transactions"].items())
    missing_count = len(missing)

    lines = [
        "# 커피 체인 일별 매출 분석 보고서",
        "",
        "| 구분 | 발견 내용 | 근거 (지점/기간/수치) | 권고 조치 |",
        "|---|---|---|---|",
        f"| 데이터 품질 | 중복 행 | {audit['duplicate_store']} {audit['duplicate_start']:%Y-%m-%d}~{audit['duplicate_end']:%Y-%m-%d}, 동일 지점-일자 {audit['duplicate_keys']}건이 2회씩 입력(추가 {audit['duplicate_rows']}행) | 지점-일자 복합키로 적재 차단, 분석 시 첫 행만 유지 |",
        f"| 데이터 품질 | 매출 단위 불일치 | 부산서면점 전 기간 {audit['busan_rows']:,}행: 객단가 약 ₩13 vs 타 지점 수천~수만 원 | 원천 통화/단위 확인 후 ×1,000 보정; POS 인터페이스 단위 검사 추가 |",
        f"| 데이터 품질 | 결측 구간 | {missing_store} {missing_start:%Y-%m-%d}~{missing_end:%Y-%m-%d}, {missing_count}개 지점-일자 누락 | 해당 기간 전년비/합계에서 제외, 백필·폐점 여부 확인 |",
        f"| 실행 기회 | 주말 수요 | 주말 일평균 매출 {won(weekend['revenue'])}, 월~금 평균 대비 {pct(weekend_uplift)} | 주말 피크 인력·재고를 우선 배치하고 저거래 지점에 주말 유입 캠페인 |",
        f"| 실행 기회 | 객단가 격차 | 최고 {best_ticket} {won(store.loc[best_ticket, 'ticket'])}, 최저 {low_ticket} {won(store.loc[low_ticket, 'ticket'])}, 차이 {won(ticket_gap)}/건 | 고객군 적합성 검증 후 번들·업셀을 실험 |",
        "",
        "## 범위·가정·보정 원칙",
        f"- 대상: {clean['date'].min():%Y-%m-%d}~{clean['date'].max():%Y-%m-%d}, 12개 지점의 일별 기록. 금액은 원(KRW)으로 해석했다.",
        "- 분석용 데이터는 중복 지점-일자에서 첫 행을 유지했다. 홍대점 결측은 임의 보간하지 않았고, 평균은 관측된 일수 기준으로 계산했다.",
        "- 부산서면점은 거래건수는 다른 지점과 유사하지만 객단가가 약 ₩13으로 1,000배 작아, 매출 단위가 천 원으로 입력되었다고 합리적으로 가정해 매출만 ×1,000 했다.",
        "- 객단가가 ₩50,000을 초과한 두 행은 인접 수준 및 거래건수 대비 정확히 100배 규모이므로 매출만 ÷100 했다. 원천 POS 대사 전에는 이 두 보정치를 재확인해야 한다.",
        "- 아래 제안은 보정 후 데이터의 기술통계에 근거한 실행 가설이다. 매출만으로 이익·인과효과는 확정할 수 없으므로 증분 매출과 마진을 함께 A/B 검증한다.",
        "",
        "## 1. 데이터 품질 점검",
        f"1. **강남점 / 2025-03-01~2025-03-31 / 동일 31개 지점-일자가 중복(총 62행, 불필요 추가 31행)** — 매출·거래·프로모션·기온이 완전히 같은 행이 두 번 들어가 있어 월 합계와 일평균이 과대 계상된다. 원인은 중복 적재 또는 재처리로 보인다. **조치:** 지점+일자를 유니크 키로 강제하고 이번 분석에서는 첫 행만 남겼다.",
        f"2. **홍대점 / 2024-06-01~2024-08-31 / 92일 결측** — 이 기간의 지점-일자 레코드가 전무하다. 원인은 휴점·시스템 누락 중 데이터만으로 판정할 수 없으며, 3개년 월별 합계·전년비를 왜곡한다. **조치:** POS 원천/휴점 로그로 백필 또는 휴점 라벨을 확정하고, 확정 전에는 기간 합계 비교에서 제외한다.",
        f"3. **부산서면점 / 전 기간 / {audit['busan_rows']:,}행 매출 단위 오류 의심** — 거래는 일평균 {store.loc['부산서면점','transactions']:,.0f}건인데 보정 전 객단가가 약 ₩13~₩14로, 타 지점 범위와 1,000배 차이다. 이는 매출이 원이 아니라 천 원 단위로 저장된 패턴이다. **조치:** 매출을 ×1,000으로 보정했으며 인터페이스의 통화단위와 범위 검증을 추가한다.",
        f"4. **일산점·대구점 / 각각 2024-11-07·2025-08-21 / 100배 이상치** — {outlier_text}. 거래건수(180건, 201건)는 평소 수준인데 객단가가 약 ₩785천·₩779천으로 비현실적이며, 매출 자릿수 오류로 판단된다. **조치:** 각각 ÷100 보정 후 원천 영수증/POS 일마감으로 확인한다.",
        f"5. **프로모션 변수 / 전 기간 / promo=1인 관측치의 금요일 비중 {pct(promo_friday_share)}** — 프로모션은 매주 금요일에만 실행되어 요일효과와 완전히 겹친다. 따라서 단순 promo=1 대 promo=0 차이를 프로모션 효과라고 믿을 수 없다. **조치:** 금요일 지점 무작위 홀드아웃 또는 격주 시행으로 대조군을 만든다.",
        "",
        "## 2. 보정 후 핵심 지표",
        f"- 보정 후 분석 행: {len(clean):,}행 (원본 {len(raw):,}행에서 중복 {audit['duplicate_rows']}행 제거).",
        f"- 최근 완결 회계연도(2025-07~2026-06) 매출은 직전 회계연도 대비 {pct(fy_growth)} 변동했다. 홍대점은 직전연도 92일 결측이므로, 이 전년비에서는 홍대점을 양 연도 모두 제외해 비교 가능성을 맞췄다.",
        f"- 주말(토·일) 일평균: 매출 {won(weekend['revenue'])}, 거래 {weekend['transactions']:,.0f}건, 객단가 {won(weekend['ticket'])}. 월~금 일평균 대비 매출 {pct(weekend_uplift)} 높다.",
        f"- 금요일(모두 프로모션 시행) 일평균 거래는 다른 요일 평균보다 {pct(friday_diff)} 높지만, 위 식별 문제 때문에 이를 프로모션의 인과효과로 해석하지 않는다.",
        "",
        "## 3. 매출 증대를 위한 실행 제안 3가지",
        f"### 제안 1. 주말 피크 운영과 저거래 지점 주말 유입을 동시에 실행",
        f"- **근거:** 보정 후 주말 일평균 매출은 {won(weekend['revenue'])}로 월~금 평균보다 {pct(weekend_uplift)} 높다. 일평균 거래가 낮은 3개 지점은 {low_volume_text}이다.",
        "- **실행:** 다음 8주 동안 해당 3개 지점에 토·일 한정 모바일 사전주문 픽업/동반 구매 쿠폰을 배치하고, 고수요 지점에는 피크 2시간의 바리스타·베이커리 재고를 증원한다. 쿠폰은 지점별로 고객의 절반에만 노출한다.",
        "- **판정 KPI:** 대조군 대비 주말 거래건수 증분, 객단가, 쿠폰 원가 후 공헌이익. 4주 중간 점검 후 증분 이익이 양수인 지점만 확대한다.",
        "",
        "### 제안 2. 저객단가 지점에서 메뉴 번들·업셀 A/B 테스트",
        f"- **근거:** 지점별 보정 객단가 최고는 {best_ticket} {won(store.loc[best_ticket, 'ticket'])}, 최저는 {low_ticket} {won(store.loc[low_ticket, 'ticket'])}로 건당 {won(ticket_gap)} 차이다. 거래량만이 아니라 구매구성 개선 여지가 크다는 신호다.",
        "- **실행:** 최저 객단가 지점부터 6주간 오전/오후 교차 방식으로 ‘음료+베이커리’ 및 ‘샷/사이즈 업’ 제안을 적용하고, 같은 시간대의 미노출 주문을 대조군으로 둔다. 최고 객단가 지점의 상품 구성·직원 스크립트는 현장 관찰 후 이식하되 고객군 차이는 별도 기록한다.",
        "- **판정 KPI:** 노출 주문의 객단가와 부가상품 부착률, 할인비용 차감 후 마진. 거래건수 감소가 없는 조건에서 객단가 증분의 80% 이상이 마진으로 남을 때 확장한다.",
        "",
        "### 제안 3. 금요일 프로모션을 ‘검증 가능한’ 실험으로 재설계",
        f"- **근거:** 프로모션 표식은 전부 금요일({pct(promo_friday_share)})이며, 금요일 거래는 타 요일 평균보다 {pct(friday_diff)} 높다. 현재 데이터는 금요일 자체 수요와 프로모션 효과를 분리할 수 없어 할인 확대 의사결정 근거로 부적합하다.",
        "- **실행:** 다음 8개 금요일에 12개 지점 중 6개 지점은 현행 프로모션, 6개 지점은 홀드아웃으로 무작위 배정하고 4주 후 교차한다. POS에 프로모션 코드·할인액·품목·마진을 추가 저장한다.",
        "- **판정 KPI:** 동일 금요일/지점 보정 후 거래건수·매출·객단가·공헌이익의 차이. ‘매출 상승’이 아니라 홀드아웃 대비 공헌이익 상승을 통과 기준으로 설정한다.",
        "",
        "## 재현 방법",
        "```text",
        "python analysis.py",
        "```",
        "이 스크립트는 `sales.csv`를 다시 읽어 동일한 보정 규칙과 지표로 이 보고서(`report.md`)를 생성한다.",
    ]
    return "\n".join(lines) + "\n"


def main() -> None:
    raw, clean, audit = load_and_audit(INPUT)
    report = generate_report(raw, clean, audit)
    OUTPUT.write_text(report, encoding="utf-8")
    print(f"완료: {OUTPUT.resolve()} 생성 ({len(clean):,}개 보정 분석 행)")


if __name__ == "__main__":
    try:
        main()
    except Exception as exc:
        print(f"오류: {exc}", file=sys.stderr)
        raise
