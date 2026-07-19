# Apple Korea 첫 화면 클론 검증

검증일: 2026-07-18

## 생성 산출물
- `index.html` — CSS와 핵심 제품 일러스트를 모두 인라인으로 포함한 단일 파일

## 브라우저 확인
- 대상: `file:///E:/ax/PRJs/gpt56-scaling/runs/test2b/luna_max/index.html`
- 브라우저 접근성 스냅샷에서 제목 `Apple (대한민국)` 및 상단 내비게이션/제품 섹션 확인
- 데스크톱 브라우저 캡처에서 다음 구조를 시각 확인:
  - 44px Apple 스타일 글로벌 내비게이션
  - 하늘색 MacBook Air 히어로
  - 밝은 회색 iPhone 히어로
  - 하늘색 iPad 히어로
  - 이후 2열 검정/밝은 타일 제품 섹션
  - Apple 스타일 푸터 링크 컬럼
- 콘솔/DOM 점검 결과:
  - `title`: `Apple (대한민국)`
  - 실행 viewport: `1262 x 624`
  - `document.documentElement.scrollWidth`: `1262`
  - `document.documentElement.clientWidth`: `1262`
  - 가로 overflow: `false`
  - 콘솔 에러: 없음
- 필수 DOM 텍스트 포함 확인:
  - `MacBook Air`, `iPhone`, `스토어`, `iPad`, `Watch`, `AirPods`, `고객지원`, `구입하기` 모두 `true`

## 모바일 대응
- `@media (max-width:700px)`에서 모바일 내비게이션으로 전환
- 375px 기준으로 히어로/제품 일러스트를 `transform: scale()`로 축소하고, 제품 타일을 1열로 전환
- `body { overflow-x:hidden }`, 모든 주요 폭은 viewport 기준으로 제한하여 가로 스크롤을 방지
- 외부 이미지/폰트/스크립트 요청이 없어서 네트워크 차단 상태에서도 렌더링 가능

## 삽질/해결
- 원본 제품 사진을 외부 URL로 연결하면 네트워크 차단 시 빈 영역이 될 수 있어 사용하지 않음
- 대신 CSS gradient, pseudo-element, border, transform으로 MacBook/휴대폰/iPad 형태를 인라인 재현
- Apple 로고는 텍스트 의존 없이 CSS shape으로 처리
- 초기 구조를 원본과 동일한 순서(상단 3개 풀폭 히어로 → 2열 제품 타일 → 푸터)로 유지해 첫 화면 비교가 잘 되도록 구성
