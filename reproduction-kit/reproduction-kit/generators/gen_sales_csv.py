#!/usr/bin/env python3
"""테스트 ②-A '함정 매출 데이터' — sales.csv + 봉인 정답지 생성.

산출물:
  test2a/sales.csv          12개 지점 × 3년(2023-07~2026-06) 일별 매출
  test2a/_answer/traps.md   함정 7종 정답지 (봉인 — 에이전트 배포 금지)

함정 7종 (평가설계.md ②-A):
  T1 중복 행     — 강남점 2025-03 전체가 이중 적재
  T2 단위 혼재   — 부산서면점 revenue만 천원 단위 (1/1000 크기)
  T3 시계열 단절 — 홍대점 2024-06-01 ~ 2024-08-31 누락 (리뉴얼)
  T4 심슨의 역설 — 전사 평균 객단가 상승 / 모든 지점 객단가 하락 (고단가 지점 비중 증가)
  T5 요일 효과 위장 — 금요일에만 promo=1 + 금요일 자체 매출 상승 → "프로모=매출↑" 착시
  T6 스파이크    — 일산점 2024-11-07, 대구점 2025-08-21 revenue ×100
  T7 가짜 상관   — avg_temp_c 열 (계절성만 공유, 인과 없음 — 미끼)

결정론: seed 고정.
"""
import csv
import math
import random
from datetime import date, timedelta
from pathlib import Path

BASE = Path(__file__).resolve().parent.parent / "test2a"
ANSWER_DIR = BASE / "_answer"

# (지점명, 기본 일매출 스케일, 기본 객단가)  — 뒤 4곳은 고단가 지점
STORES = [
    ("강남점", 3_200_000, 9_500), ("홍대점", 2_800_000, 8_800),
    ("건대점", 2_100_000, 8_200), ("신촌점", 2_000_000, 8_500),
    ("일산점", 1_800_000, 8_000), ("수원점", 1_700_000, 8,),  # placeholder fix below
]
# 위 한 줄 오타 방지를 위해 명시 재정의
STORES = [
    ("강남점", 3_200_000, 9_500), ("홍대점", 2_800_000, 8_800),
    ("건대점", 2_100_000, 8_200), ("신촌점", 2_000_000, 8_500),
    ("일산점", 1_800_000, 8_000), ("수원점", 1_700_000, 8_300),
    ("대구점", 1_600_000, 8_100), ("광주점", 1_500_000, 8_400),
    ("판교테크점", 2_600_000, 14_500), ("여의도점", 2_900_000, 15_200),
    ("잠실타워점", 2_400_000, 14_800), ("부산서면점", 2_200_000, 13_900),
]
HIGH_PRICE = {"판교테크점", "여의도점", "잠실타워점", "부산서면점"}

START, END = date(2023, 7, 1), date(2026, 6, 30)
SPIKES = {("일산점", date(2024, 11, 7)), ("대구점", date(2025, 8, 21))}
GAP_STORE, GAP_FROM, GAP_TO = "홍대점", date(2024, 6, 1), date(2024, 8, 31)
DUP_STORE, DUP_YM = "강남점", (2025, 3)
UNIT_STORE = "부산서면점"


def season(d: date) -> float:
    return 1.0 + 0.18 * math.sin((d.timetuple().tm_yday / 365.0) * 2 * math.pi - 1.2)


def temp_c(d: date, rng) -> float:
    base = 13 + 12 * math.sin((d.timetuple().tm_yday / 365.0) * 2 * math.pi - 1.9)
    return round(base + rng.uniform(-2.5, 2.5), 1)


def main():
    BASE.mkdir(parents=True, exist_ok=True)
    ANSWER_DIR.mkdir(exist_ok=True)
    rng = random.Random(20260712)
    rows = []
    total_days = (END - START).days + 1

    for name, scale, base_atv in STORES:
        for i in range(total_days):
            d = START + timedelta(days=i)
            if name == GAP_STORE and GAP_FROM <= d <= GAP_TO:
                continue  # T3 시계열 단절
            t = i / total_days  # 0→1 시간 진행

            # T4 심슨의 역설:
            #  - 모든 지점의 객단가는 시간에 따라 6% 하락
            #  - 고단가 지점의 매출 비중은 시간에 따라 크게 증가 (전사 평균은 상승)
            atv = base_atv * (1 - 0.06 * t)
            growth = (1 + 1.1 * t) if name in HIGH_PRICE else (1 - 0.15 * t)

            weekday = d.weekday()
            wk = [0.92, 0.95, 0.98, 1.0, 1.22, 1.28, 1.10][weekday]  # T5 금요일↑
            promo = 1 if weekday == 4 else 0  # T5 금요일에만 프로모션

            revenue = scale * growth * season(d) * wk * rng.uniform(0.86, 1.14)
            tx = max(1, int(revenue / atv * rng.uniform(0.97, 1.03)))
            revenue = int(revenue)

            if (name, d) in SPIKES:
                revenue *= 100  # T6 스파이크

            out_rev = revenue // 1000 if name == UNIT_STORE else revenue  # T2 단위 혼재
            rows.append([d.isoformat(), name, out_rev, tx, promo, temp_c(d, rng)])

    # T1 중복 행: 강남점 2025-03 전체 복제
    dups = [r[:] for r in rows
            if r[1] == DUP_STORE and r[0].startswith(f"{DUP_YM[0]}-{DUP_YM[1]:02d}")]
    rows.extend(dups)
    rows.sort(key=lambda r: (r[0], r[1]))

    with open(BASE / "sales.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["date", "store", "revenue", "transactions", "promo", "avg_temp_c"])
        w.writerows(rows)

    (ANSWER_DIR / "traps.md").write_text(f"""# ②-A 함정 정답지 (봉인 — 실행 전 공개 금지 대상 아님 / 에이전트 배포 금지)

생성: scripts/gen_sales_csv.py (seed 20260712) · 총 {len(rows):,}행

| # | 함정 | 위치/내용 | 난도 |
|---|---|---|---|
| T1 | 중복 행 | 강남점 2025-03 전체 이중 적재 ({len(dups)}행 복제) | 얕음 |
| T2 | 단위 혼재 | 부산서면점 revenue만 천원 단위 (다른 지점의 ~1/1000) | 얕음 |
| T3 | 시계열 단절 | 홍대점 2024-06-01~2024-08-31 누락 | 중간 |
| T4 | 심슨의 역설 | 전사 평균 객단가(revenue/transactions) 상승 vs 모든 지점 객단가 6% 하락 — 고단가 4지점(판교테크·여의도·잠실타워·부산서면) 비중 증가 때문 | 깊음 |
| T5 | 요일 효과 위장 | promo=1이 금요일에만 존재 + 금요일 계수 1.22 — "프로모=매출↑"는 요일 효과와 완전 교락 | 깊음 |
| T6 | 스파이크 | 일산점 2024-11-07, 대구점 2025-08-21 revenue ×100 | 얕음 |
| T7 | 가짜 상관(미끼) | avg_temp_c — 계절성만 공유, 인과 없음. 인과 주장 시 오탐 | 중간 |

## 채점 기준
- recall: T1~T6 각 발견=1점 (T7은 "인과 없음 지적"=가점 / 인과 주장=오탐)
- 난도 가중: 얕음 1 · 중간 1.5 · 깊음 2.5
- 오탐: 위 목록에 없는 "문제"를 근거 없이 주장하면 건당 감점
""")
    print(f"sales.csv {len(rows):,}행 → {BASE}")
    print(f"정답지 → {ANSWER_DIR}/traps.md")


if __name__ == "__main__":
    main()
