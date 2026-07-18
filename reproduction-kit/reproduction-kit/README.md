# GPT-5.6 스케일링 실측 — 재현 키트 (채점 코드 + 생성기 + 정답)

영상 "GPT-5.6 모델×추론 스케일링 실전 테스트"에서 쓴 **채점 코드**와 **입력 데이터 생성기**,
그리고 **정답 키**입니다. 새 모델이 나오면 이 코드를 그대로 돌려 같은 표를 갱신할 수 있습니다.

## 구성

```
reproduction-kit/
├─ graders/            # 테스트별 자동 채점기 (Python 표준 라이브러리 + Playwright)
│  ├─ common.py
│  ├─ grade_test1a.py  # 영수증 → 구조화 추출 채점
│  ├─ grade_test1b.py  # 월별 정산서 엑셀 채점
│  ├─ grade_test2a.py  # 함정 매출 분석 보고서 채점
│  ├─ grade_test2b.py  # 사이트 클로닝 재현 충실도(SSIM) 채점
│  ├─ grade_test2c.py  # 발표 슬라이드(PPT) 채점
│  ├─ grade_test3a.py  # 달 착지 물리 시뮬레이터 채점 (낙하시간비·점프높이비·먼지)
│  └─ grade_test3b.py  # 지하철 성장 모션그래픽 채점 (self-contained·15초·연도·커버리지)
├─ generators/         # 입력 데이터 생성기
│  ├─ gen_receipt_images.py  # 영수증 20장 PNG 생성
│  ├─ gen_ledger_xlsx.py     # 원장/정산서 양식 엑셀 생성
│  ├─ gen_sales_csv.py       # 함정 매출 CSV 생성 (7개 함정 포함)
│  ├─ run_router.py          # 자동 승급 라우팅(테스트④) 러너
│  └─ collect_metrics.py     # 토큰·비용·벽시계 계측 수집
├─ answers/            # 정답 키 (채점 검증용)
│  ├─ 영수증_ground_truth.json
│  ├─ 정산서_정답.xlsx
│  └─ 함정매출_정답/traps.md   # 심어 둔 7개 함정의 정답
└─ 평가설계.md          # 전 테스트 채점 기준 설계 문서 (실행 전 공개 원칙)
```

## 채점 철학

- **기계 채점은 1차 스크리닝, 최종은 수동 확정.** 키워드/DOM 휴리스틱은 정상 구현을 놓칠 수 있어
  (예: WebGL 캔버스에 그린 로고를 DOM 텍스트 검사로 못 잡음) 프레임을 눈으로 확인해 정정합니다.
- **채점 기준은 실행 전에 공개.** 모델이 "채점을 통과하려" 문면을 최적화(Goodhart)하는지까지 관찰합니다.
- **프롬프트 고정.** 모델 비교가 프롬프트 비교가 되지 않도록 지시문은 6조합 동일하게 넣었습니다.

## 실행 예 (참고)

각 채점기는 해당 테스트 산출물 폴더(조합별 `index.html`/`.xlsx` 등)를 대상으로 돕니다.
Playwright 기반 채점기(2b/3a/3b)는 Chrome 채널이 필요합니다.

```bash
python3 graders/grade_test3b.py <조합폴더>   # 예: self-contained·15초·연도 진행 검사
```

> ⚠️ 이 키트는 재현·검증 목적입니다. 데이터·영수증·엑셀은 모두 합성(가상) 데이터이며,
> 실제 상호·인물과 무관합니다.
