# Verification

- Target: standalone `index.html` (external network dependency 없음).
- Playwright Chromium으로 `file:///.../index.html` 렌더를 확인했습니다.
- Desktop viewport: 1440 × 900 — Apple 스타일의 44px 상단 탐색, MacBook Air 히어로 및 이어지는 iPhone 섹션을 확인했습니다.
- Mobile viewport: 375 × 812 — 모바일 탐색 바와 단일 열 레이아웃을 확인했습니다.
- 자동 점검: 두 viewport 모두 `scrollWidth === clientWidth`, browser console error 0건.

## 구현/해결 메모

- 제품 사진의 네트워크 의존성을 없애기 위해 노트북, iPhone, iPad, Watch 및 AirPods를 CSS 도형/그라디언트로 직접 구성했습니다.
- 환경에 따라 Apple 전용 글리프가 누락되는 문제를 피하려고 상단 로고는 인라인 SVG로 구성했습니다.
- 스크린샷 산출물 `desktop.png`, `mobile.png`은 로컬 육안 점검용입니다.
