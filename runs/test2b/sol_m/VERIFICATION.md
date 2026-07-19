# Apple Korea Homepage Clone — Verification

검증 일시: 2026-07-18
기준 원본: https://www.apple.com/kr/
기준 뷰포트: 1440 × 900 CSS px
모바일 뷰포트: 375 × 812 CSS px
검증 브라우저: Microsoft Edge Chromium, Playwright headless

## 최종 판정

| 달성 기준 | 결과 | 실행 근거 |
|---|---|---|
| 1. `index.html` 단일 웹 산출물 존재 | PASS | `index.html` 1,556,847 bytes, 모든 CSS·제품 이미지를 파일 내부에 포함 |
| 2. 헤드리스 브라우저 콘솔 에러 0건 | PASS | 1440px 및 375px 로드에서 `console.error` 0건, `pageerror` 0건 |
| 3. 1440px 스크린샷 캡처 및 원본 비교 | PASS | `clone-1440.png` 캡처 완료, `original-1440.png`와 아래 항목으로 비교 |
| 4. 375px에서 가로 스크롤 없음 | PASS | `scrollWidth=375`, `clientWidth=375`, `bodyScrollWidth=375` |

## 자동 검증 결과

### 1440px 복제본

- 문서 제목: `Apple (대한민국)`
- 문서 너비: `scrollWidth=1440`, `clientWidth=1440`
- 전체 높이: `5014px`
- 콘솔 에러: 0
- 페이지 에러: 0
- 채점 텍스트 확인: MacBook Air, iPhone, 스토어, iPad, Watch, AirPods, 고객지원, 구입하기 — 모두 존재

### 375px 복제본

- 문서 너비: `scrollWidth=375`, `clientWidth=375`, `bodyScrollWidth=375`
- 전체 높이: `5937px`
- 가로 오버플로: 없음
- 콘솔 에러: 0
- 페이지 에러: 0
- 채점 텍스트 8개: 모두 존재

## 1440px 원본 비교 메모

비교 파일:

- 원본: `original-1440.png` — 원본 페이지 전체 높이 5,247px
- 복제본: `clone-1440.png` — 복제 페이지 전체 높이 5,014px

비교 결과:

- 상단 글로벌 내비게이션은 44px 높이, 중앙 1024px 폭, Apple 로고·제품군·검색·쇼핑백 배열을 재현했다.
- MacBook Air, iPhone, iPad Air의 3개 580px 히어로 섹션은 원본 제품 이미지, 배경색, 중앙 제목·부제·알약형 CTA 구성을 재현했다.
- 본문 프로모션은 원본처럼 2열, 12px 간격, 각 580px 높이로 구성했고 MacBook Pro, AirPods Pro 3, Apple Watch Series 11, iPad Pro, Apple Watch Ultra 3, Apple Trade In 순서를 유지했다.
- Apple TV 갤러리는 대표 포스터, 시청 CTA, 설명과 페이지 도트 구조를 재현했다. 원본의 자동 슬라이드 동작은 정적 단일 HTML 요구와 첫 프레임 시각 재현을 우선해 제외했다.
- 푸터는 각주, 5열 디렉토리, 쇼핑 안내, 법적 링크, 회사 정보를 원본과 동일한 회색 톤과 정보 계층으로 재현했다.
- 복제본이 원본보다 약 233px 짧다. 주된 차이는 원본 Apple TV 캐러셀의 주변 여백/프레임과 긴 법적 각주를 압축한 데서 발생한다. 핵심 구조와 첫 화면 및 제품 섹션의 높이·배치는 일치한다.
- 원본 제품 이미지를 데이터 URI로 내장했으므로 네트워크 없이 동일한 이미지가 렌더링된다.

## 모바일 시각 점검

- 375px에서 내비게이션은 Apple 로고, 검색, 쇼핑백, 메뉴 아이콘만 표시한다.
- 히어로와 프로모션은 1열 500px 카드로 전환되며 모바일 전용 제품 이미지를 사용한다.
- 제목, CTA, 제품 이미지의 겹침이나 잘림이 없고 섹션 사이 12px 구분을 유지한다.
- 푸터 디렉토리는 모바일용 접이식 행 형태로 축약 표시한다.

## 구현 가정

1. “단일 HTML 파일”은 웹 페이지 실행 산출물이 `index.html` 하나라는 뜻으로 해석했다. 검증 기록과 스크린샷은 실행 의존성이 아닌 검증 증거로 별도 보관한다.
2. 외부 의존을 만들지 않기 위해 폰트 CDN도 사용하지 않고 시스템 Apple 계열 폰트를 사용했다. 모든 제품 이미지는 `index.html` 안의 base64 데이터 URI로 내장했다.
3. 팝업, 쿠키 공지, 지역 선택 모달은 닫힌 상태 기준으로 제외했다.
4. 링크는 시각 복제와 단일 파일의 오프라인 동작을 우선해 페이지 내 더미 앵커로 구성했다.
5. 원본의 자동 재생 캐러셀과 드롭다운 메뉴 JavaScript는 콘솔 에러 없는 정적 복제를 위해 제외했다.

## 파일 무결성

- `index.html` SHA-256: `6c59e8f9b956f7c253f099bb64583656de66fbb4f524c45aa1c308e8fdaed652`
