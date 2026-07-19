# VERIFICATION.md

검증 일시: 2026-07-19 KST  
대상: `index.html`  
브라우저: Chromium (Playwright 1.61.1), headless  
뷰포트: 1080×1920, deviceScaleFactor 1

## 실행 방법

```bash
node verify.mjs
```

검증기는 로컬 `file:///.../index.html`을 열고 console/pageerror/request를 감시한 뒤, 실제 rAF 실행을 15초 이상 관측했습니다. 결과 원문은 작업 중 `verification-results.json`에 저장해 확인했습니다.

## 달성 기준 자체 점검

| 기준 | 결과 | 실행 증거 |
|---|---|---|
| 단일 실행 파일 | PASS | 동작에 필요한 HTML/CSS/JS/데이터/폰트가 `index.html` 하나에 내장됨 |
| 외부 리소스 요청 없음 | PASS | HTTP/HTTPS request 0건. 전체 request는 로컬 `index.html` 1건뿐 |
| 1080×1920 고정 스테이지 | PASS | canvas `[1080,1920]`, viewport `[1080,1920]`, stage rect `[0,0,1080,1920]` |
| 스크롤 없음 | PASS | document scroll size `[1080,1920]`, `overflow: hidden` |
| 오디오 없음 | PASS | audio/video 요소 및 Web Audio 사용 없음 |
| requestAnimationFrame 기반 | PASS | `requestAnimationFrame(frame)` 실동작 관측 |
| 15.0초 완결 | PASS | 최종 계측값 `{t:15, year:2026, lines_shown:19}` |
| 이후 정지 화면 유지 | PASS | 0.6초 간격의 두 최종 PNG SHA-256 및 `__mg`가 동일 |
| 매 프레임 `window.__mg` 갱신 | PASS | 실제 시퀀스가 단조 증가하며 최종 프레임에서 t=15로 고정 |
| 진행 연도 1974→2026 | PASS | 첫 상태 1974, 최종 상태 2026 |
| 시작부터 흐린 전체 가이드 | PASS | 활성 노선 draw보다 먼저 모든 19개 path를 저명도 렌더링; t=0 코드/프레임 확인 |
| 연도별 노선 성장 | PASS | 노선별 개통연도를 13.7초 타임스케일에 매핑하고 0.60초 draw reveal 적용 |
| 일반역/환승역 구분 | PASS | 일반역 실점, 환승역 흰색 이중 링 |
| 주요 역 라벨 | PASS | 서울역·잠실·강남·왕십리·여의도·김포공항이 각 개통 시점에 등장 |
| 마지막 약 1초 완성 화면 | PASS | 마지막 노선 draw는 약 13.77초 완료, 15.0초까지 약 1.23초 유지 |
| 콘솔 오류 0건 | PASS | console error `[]`, pageerror `[]` |
| 시각 검수 | PASS | 1080×1920 최종 PNG에서 잘림 없음, 6개 라벨 충돌 완화, 제목/연도/타임라인/범례 가독성 확인 |
| 출처·가공 기록 | PASS | `SOURCES.md`에 URL, OSM relation ID, 쿼리, 라이선스, 가공 방법, 수량 기록 |

## `window.__mg` 실제 시퀀스

첫 rAF는 내장 폰트가 준비된 뒤 시작하므로 `wall_s`와 애니메이션 `t` 사이에 약 0.1초의 초기화 차이가 있습니다. 요구 시간은 rAF 기준 `t`입니다.

| wall_s | t | year | lines_shown |
|---:|---:|---:|---:|
| 0.086 | 0.000 | 1974 | 0 |
| 1.015 | 0.900 | 1977 | 1 |
| 3.007 | 2.883 | 1984 | 2 |
| 5.010 | 4.883 | 1992 | 4 |
| 7.509 | 7.400 | 2002 | 8 |
| 10.007 | 9.900 | 2011 | 12 |
| 12.512 | 12.383 | 2021 | 17 |
| 14.003 | 13.866 | 2026 | 19 |
| 15.060 | 14.933 | 2026 | 19 |
| final | 15.000 | 2026 | 19 |
| final + 0.6s | 15.000 | 2026 | 19 |

`lines_shown`은 선이 그려지기 시작한 노선 수입니다. 최초 t=0 프레임에서 1호선의 draw progress가 정확히 0이므로 0이며, 다음 rAF부터 1이 됩니다. 흐린 전체 가이드는 t=0부터 19개 노선 모두 표시됩니다.

## 정지 화면 해시

- 최종 PNG 1 SHA-256: `fe1a172301f48d69193b81a7f3e8f9a44a326877a08ea4d422b7f2fb588dd8a7`
- 0.6초 뒤 PNG 2 SHA-256: `fe1a172301f48d69193b81a7f3e8f9a44a326877a08ea4d422b7f2fb588dd8a7`
- 판정: 동일 — rAF 종료 후 화면 유지

## 런타임 요청·오류 원문 요약

```json
{
  "console_errors": [],
  "page_errors": [],
  "external_requests": [],
  "all_requests": [
    "file:///E:/ax/PRJs/gpt56-scaling/runs/test3b/sol_h/index.html"
  ],
  "final_state_1": {"t":15,"year":2026,"lines_shown":19},
  "final_state_2": {"t":15,"year":2026,"lines_shown":19},
  "final_static": true,
  "fontStatus": "loaded"
}
```

## 최종 수량

- 노선: 19
- 이름 기준 역 마커: 555
- 환승역 마커: 96
- 애니메이션 연도: 1974–2026
- 실제 노선 개통 이정표: 1974–2024
- 최종 HTML 크기: 194,406 bytes

## 결론

모든 필수 기준을 실행으로 확인했으며 실패 항목은 없습니다.
