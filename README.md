# GPT-5.6 Scaling Lab 따라 하기 가이드

이 저장소의 목적은 단순합니다.

**GPT-5.6 모델x추론 스케일링 실험에 사용된 7가지 벤치마크 테스트를 누구나 쉽게, 스텝 바이 스텝으로 따라 해 볼 수 있게 만드는 것**입니다.

단테랩스 원문, 입력 데이터, 재현 키트, 채점 코드를 한곳에 모아 두었고, 이 README는 처음 보는 사람도 같은 테스트를 다시 실행해 볼 수 있도록 안내합니다.

## 무엇을 해 보는 프로젝트인가

이 프로젝트는 모델에게 7가지 실무형 과제를 맡긴 뒤, 결과물을 파일로 저장하고, 제공된 채점기로 품질을 확인하는 벤치마크 재현 키트입니다.

7가지 테스트는 다음과 같습니다.

| 번호 | 테스트 | 모델이 만들어야 하는 산출물 |
| --- | --- | --- |
| 1A | 영수증 이미지 구조화 추출 | `receipts.json` |
| 1B | 거래 원장 기반 정산서 작성 | `정산서_완성.xlsx` |
| 2A | 함정 매출 데이터 분석 보고서 | `report.md`, `analysis.py` |
| 2B | Apple Korea 페이지 클론 | `index.html`, `VERIFICATION.md` |
| 2C | 10분 발표용 PPT 제작 | `deck.pptx`, `preview/` |
| 3A | 지구 vs 달 착지 물리 시뮬레이션 | `index.html`, `VERIFICATION.md` |
| 3B | 서울 지하철 성장 모션그래픽 | `index.html`, `SOURCES.md`, `VERIFICATION.md` |

## 이 가이드의 실행 계획

이 README는 아래 계획에 맞춰 구성되어 있습니다.

1. 저장소 안에 무엇이 들어 있는지 확인한다.
2. 공통 실행 환경을 준비한다.
3. 입력 데이터와 과제 지시문을 확인한다.
4. 테스트별 작업 폴더를 만든다.
5. 각 테스트의 프롬프트를 모델에게 전달한다.
6. 모델이 만든 산출물을 작업 폴더에 저장한다.
7. 대응하는 채점기를 실행한다.
8. 점수와 실패 원인을 기록하고, 필요하면 다시 수정한다.
9. 여러 모델/추론 설정으로 반복 실행해 비용과 품질을 비교한다.

처음에는 1A 또는 1B처럼 입력과 산출물이 명확한 테스트부터 시작하는 것을 추천합니다. 이후 웹/시뮬레이션/PPT처럼 환경 의존성이 큰 테스트로 확장하면 흐름을 잡기 쉽습니다.

## 폴더 구조

```text
.
├─ README.md
├─ PROJECT_ANALYSIS.md
├─ prompt.md
├─ 입력데이터.zip
├─ 입력데이터/
│  ├─ 영수증/
│  │  ├─ R01.png
│  │  └─ ...
│  ├─ 함정매출_sales.csv
│  ├─ 원장_ledger.xlsx
│  └─ 정산서_양식.xlsx
├─ reproduction-kit.zip
├─ reproduction-kit/
│  └─ reproduction-kit/
│     ├─ graders/
│     └─ generators/
├─ dante-labs-gpt56-scaling-lab.html
└─ dante-labs-gpt56-scaling-lab.pdf
```

더 자세한 프로젝트 해설은 `PROJECT_ANALYSIS.md`에 정리되어 있습니다.

## 공통 준비

### 1. Python 준비

채점기는 Python으로 실행합니다. 기본적으로 Python 3.x가 필요합니다.

```bash
python --version
```

일부 채점기는 다음 패키지가 필요할 수 있습니다.

```bash
pip install openpyxl pandas pillow scikit-image numpy python-pptx playwright
python -m playwright install chromium
```

환경에 따라 `python` 대신 `python3`를 사용하면 됩니다.

### 2. 작업 폴더 만들기

모델별/테스트별 결과를 섞지 않으려면 `runs/` 아래에 별도 폴더를 만드는 방식을 추천합니다.

```bash
mkdir -p runs/test1a/my-model
mkdir -p runs/test1b/my-model
mkdir -p runs/test2a/my-model
mkdir -p runs/test2b/my-model
mkdir -p runs/test2c/my-model
mkdir -p runs/test3a/my-model
mkdir -p runs/test3b/my-model
```

Windows PowerShell에서는 다음처럼 만들 수 있습니다.

```powershell
New-Item -ItemType Directory -Force runs/test1a/my-model
```

### 3. 프롬프트 확인

벤치마크의 원문 지시문은 `prompt.md`에 있습니다. 테스트별 블록을 찾아 모델에게 전달하고, 필요한 입력 파일도 함께 제공합니다.

주의: 일부 터미널에서는 한글이 깨져 보일 수 있습니다. VS Code, Cursor, Notepad++, GitHub 웹 화면처럼 UTF-8을 잘 처리하는 편집기에서 여는 것을 권장합니다.

## 테스트 1A: 영수증 이미지 구조화 추출

목표: `입력데이터/영수증/R01.png`부터 `R20.png`까지 읽고, 영수증 20장을 JSON 배열로 구조화합니다.

### 따라 하기

1. `runs/test1a/my-model/` 폴더를 만듭니다.
2. 모델에게 `prompt.md`의 영수증 추출 테스트 지시문을 전달합니다.
3. 입력 이미지 `입력데이터/영수증/` 폴더를 함께 제공합니다.
4. 모델 산출물을 `runs/test1a/my-model/receipts.json`으로 저장합니다.
5. 채점기를 실행합니다.

```bash
python reproduction-kit/reproduction-kit/graders/grade_test1a.py --run-dir runs/test1a/my-model
```

통과 기준은 JSON 스키마 충족과 필드 정확도입니다.

## 테스트 1B: 원장 기반 정산서 작성

목표: `원장_ledger.xlsx`를 집계해 `정산서_양식.xlsx`의 빈 칸을 채운 완성본을 만듭니다.

### 따라 하기

1. `runs/test1b/my-model/` 폴더를 만듭니다.
2. `입력데이터/원장_ledger.xlsx`와 `입력데이터/정산서_양식.xlsx`를 모델에게 제공합니다.
3. `prompt.md`의 정산서 작성 테스트 지시문을 전달합니다.
4. 모델 산출물을 `runs/test1b/my-model/정산서_완성.xlsx`로 저장합니다.
5. 채점기를 실행합니다.

```bash
python reproduction-kit/reproduction-kit/graders/grade_test1b.py --run-dir runs/test1b/my-model
```

통과 기준은 엑셀 구조 유지와 값 정확도입니다.

## 테스트 2A: 함정 매출 데이터 분석

목표: `함정매출_sales.csv`를 분석해 데이터 문제를 찾고, 실행 가능한 제안 3가지를 보고서로 씁니다.

### 따라 하기

1. `runs/test2a/my-model/` 폴더를 만듭니다.
2. `입력데이터/함정매출_sales.csv`를 모델에게 제공합니다.
3. `prompt.md`의 매출 분석 테스트 지시문을 전달합니다.
4. 모델 산출물을 다음 이름으로 저장합니다.
   - `runs/test2a/my-model/report.md`
   - `runs/test2a/my-model/analysis.py`
5. 채점기를 실행합니다.

```bash
python reproduction-kit/reproduction-kit/graders/grade_test2a.py --run-dir runs/test2a/my-model
```

이 채점기는 키워드 기반 잠정 평가를 수행합니다. 최종 평가는 사람이 `report.md`를 읽고 함정 발견 여부와 오탐 여부를 확인하는 방식입니다.

## 테스트 2B: Apple Korea 페이지 클론

목표: Apple Korea 페이지를 시각적으로 비슷하게 재현한 단일 HTML 파일을 만듭니다.

### 따라 하기

1. `runs/test2b/my-model/` 폴더를 만듭니다.
2. `prompt.md`의 Apple 클론 테스트 지시문을 모델에게 전달합니다.
3. 모델 산출물을 다음 이름으로 저장합니다.
   - `runs/test2b/my-model/index.html`
   - `runs/test2b/my-model/VERIFICATION.md`
4. Playwright/Chromium 환경을 준비합니다.
5. 채점기를 실행합니다.

```bash
python reproduction-kit/reproduction-kit/graders/grade_test2b.py --run-dir runs/test2b/my-model
```

통과 기준은 DOM 기본 조건, 콘솔 오류, 1440px 기준 시각 유사도, 375px 모바일 가로 스크롤 여부 등입니다.

## 테스트 2C: 10분 발표용 PPT 제작

목표: 브리프 문서를 바탕으로 10분 발표용 슬라이드 덱을 만듭니다.

### 따라 하기

1. `runs/test2c/my-model/` 폴더를 만듭니다.
2. `prompt.md`의 PPT 제작 테스트 지시문을 모델에게 전달합니다.
3. 필요한 브리프 입력이 있다면 같은 폴더에 둡니다.
4. 모델 산출물을 다음 이름으로 저장합니다.
   - `runs/test2c/my-model/deck.pptx`
   - `runs/test2c/my-model/preview/`
5. 채점기를 실행합니다.

```bash
python reproduction-kit/reproduction-kit/graders/grade_test2c.py --run-dir runs/test2c/my-model
```

통과 기준은 PPT 파일 파싱 가능 여부, 모든 슬라이드의 제목/발표자 노트 포함 여부, 핵심 키워드 반영 여부입니다.

## 테스트 3A: 지구 vs 달 착지 물리 시뮬레이션

목표: Three.js 기반의 단일 HTML 시뮬레이션을 만들어 지구와 달의 중력 차이를 물리적으로 표현합니다.

### 따라 하기

1. `runs/test3a/my-model/` 폴더를 만듭니다.
2. `prompt.md`의 착지 시뮬레이션 테스트 지시문을 모델에게 전달합니다.
3. 모델 산출물을 다음 이름으로 저장합니다.
   - `runs/test3a/my-model/index.html`
   - `runs/test3a/my-model/VERIFICATION.md`
4. 채점기를 실행합니다.

```bash
python reproduction-kit/reproduction-kit/graders/grade_test3a.py --run-dir runs/test3a/my-model
```

통과 기준은 렌더링, 콘솔 오류, 점프/낙하 로그, 중력비 기반 물리 일관성 등입니다. 먼지나 발자국 같은 시각 요소는 수동 확인이 필요할 수 있습니다.

## 테스트 3B: 서울 지하철 성장 모션그래픽

목표: 1974년부터 2026년까지 서울 지하철 노선망이 확장되는 15초 세로 모션그래픽을 단일 HTML로 만듭니다.

### 따라 하기

1. `runs/test3b/my-model/` 폴더를 만듭니다.
2. `prompt.md`의 지하철 모션그래픽 테스트 지시문을 모델에게 전달합니다.
3. 모델 산출물을 다음 이름으로 저장합니다.
   - `runs/test3b/my-model/index.html`
   - `runs/test3b/my-model/SOURCES.md`
   - `runs/test3b/my-model/VERIFICATION.md`
4. 채점기를 실행합니다.

```bash
python reproduction-kit/reproduction-kit/graders/grade_test3b.py --run-dir runs/test3b/my-model
```

통과 기준은 단일 HTML, 외부 런타임 요청 없음, 15초 타임라인 완결, `window.__mg` 계측값, 노선 표시 진행 등입니다.

## 결과 기록 방법

여러 모델이나 추론 설정을 비교하려면 결과를 표로 남기는 것이 좋습니다.

| 테스트 | 모델/설정 | 통과 여부 | 점수/주요 지표 | 비용 | 걸린 시간 | 메모 |
| --- | --- | --- | --- | --- | --- | --- |
| 1A | 예: model-high | PASS | field acc 97% |  |  |  |
| 1B |  |  |  |  |  |  |
| 2A |  |  |  |  |  |  |
| 2B |  |  |  |  |  |  |
| 2C |  |  |  |  |  |  |
| 3A |  |  |  |  |  |  |
| 3B |  |  |  |  |  |  |

## 추천 진행 순서

처음 따라 해 본다면 아래 순서가 가장 부담이 적습니다.

1. `1A` 영수증 JSON 추출
2. `1B` 정산서 엑셀 작성
3. `2A` 매출 데이터 분석
4. `2C` PPT 제작
5. `3A` 물리 시뮬레이션
6. `3B` 지하철 모션그래픽
7. `2B` Apple 페이지 클론

앞의 세 테스트는 데이터와 산출물 구조가 명확하고, 뒤의 테스트는 브라우저 렌더링과 시각 품질 확인이 들어가므로 난이도가 올라갑니다.

## 원문과 참고 문서

- 원문 HTML 보존본: `dante-labs-gpt56-scaling-lab.html`
- 원문 PDF 보존본: `dante-labs-gpt56-scaling-lab.pdf`
- 프로젝트 분석: `PROJECT_ANALYSIS.md`
- 과제 지시문: `prompt.md`
- 재현 키트: `reproduction-kit/reproduction-kit/`

## 최종 목표

이 README의 최종 목표는 한 가지입니다.

**새 모델이나 새 추론 설정이 나왔을 때, 누구나 이 7가지 테스트를 같은 방식으로 다시 돌려 보고, 품질과 비용을 비교할 수 있게 하는 것.**

테스트를 한 번만 실행하는 것이 아니라, 결과를 기록하고 비교하면서 자신에게 맞는 모델/추론 설정을 찾는 실험 노트로 이 저장소를 활용하면 됩니다.
