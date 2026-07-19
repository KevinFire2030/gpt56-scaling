# Verification

- 구현 파일: `index.html` (외부 이미지·스크립트 의존성 없는 단일 HTML/CSS 구현)
- 브라우저에서 `file:///E:/ax/PRJs/gpt56-scaling/runs/test2b/terra_max/index.html`을 열어 렌더링을 확인했습니다.
- 데스크톱 브라우저 확인값: viewport 1262px, `document.documentElement.scrollWidth` 1262px로 가로 오버플로가 없습니다.
- 첫 화면에서 반투명 글로벌 네비게이션, 하늘색 MacBook Air 히어로, 이어지는 iPhone 제품 섹션이 보이는 것을 시각적으로 확인했습니다.
- 제품 이미지는 네트워크 차단 환경에서도 보이도록 CSS 도형/그라데이션으로 직접 구성했습니다.
- 삽질/해결: Playwright Node 패키지가 현재 런타임에 설치되어 있지 않아 로컬 브라우저 도구로 렌더링 및 DOM 폭을 검증했습니다. 모바일은 700px 이하 미디어 쿼리로 단일 열 및 작은 기기 전용 도형 크기를 지정해 가로 넘침을 방지했습니다.
