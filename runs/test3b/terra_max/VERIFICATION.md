# VERIFICATION — index.html

검증일: 2026-07-19
검증 대상: `index.html` (로컬 `file:///` URL, 헤드리스 Chromium/Playwright 및 브라우저 런타임)

| 달성 기준 | 결과 | 실제 확인값 / 방법 |
|---|---|---|
| 단일 HTML, 인라인 자산 | PASS | `index.html` 1개에 CSS, JS, 노선 데이터, Canvas 도식이 포함됨. 런타임 리소스 목록 `[]`. |
| 1080×1920 고정 스테이지, 스크롤·오디오 없음 | PASS | CSS `#stage { width:1080px; height:1920px; overflow:hidden }`; `<audio>` 및 외부 미디어 없음. |
| rAF 사용 | PASS | 일반 URL에서 `requestAnimationFrame(frame)`으로 시작하고, 프레임마다 `draw()` 실행. |
| 15.0초 완결 | PASS | 실제 일반 URL에서 15.3초 대기 후 `window.__mg = {t:15000, year:2026, lines_shown:21}`. `t`는 `Math.min(duration, …)`로 15000ms에 clamp. |
| 종료 뒤 정지 화면 | PASS | 15.0초 값과 1.1초 뒤 값 모두 `{t:15000, year:2026, lines_shown:21}`. 15초 이후 rAF를 새로 예약하지 않음. |
| 마지막 약 1초 전체망 유지 | PASS | 마지막 성장 이벤트(GTX-A)는 13,000ms에 시작, 850ms에 선형 완성; 13,850–15,000ms(1,150ms) 동안 완성망 유지. |
| 매 프레임 `window.__mg` 갱신 | PASS | `draw(t)` 끝에서 `{t,year,lines_shown}`을 대입. 일반 rAF와 수동 프레임 스텝 모두 동일 렌더 경로 사용. |
| 콘솔 오류 | PASS | headless 브라우저 콘솔 `js_errors: []`, `total_errors: 0`. |
| 외부 요청 | PASS | 일반 URL에서 `performance.getEntriesByType('resource')` 결과 `[]`. |
| 최종 프레임 시각 검수 | PASS | Playwright 16초 스크린샷으로 전체망·연도 2026·21 routes·환승 원형 마커·역명 라벨·진행 바를 육안 확인. |

## `window.__mg` 실제 시퀀스

시간 경계를 정확히 재현하기 위해 동일 `draw()` 함수를 호출하는 내장 `?manual=1` 진단 모드에서, 다음 시점을 기록했다. 일반 모드의 애니메이션 실행은 위의 15.3초 런으로 별도 확인했다.

| 요청 시각 (ms) | `t` | `year` | `lines_shown` |
|---:|---:|---:|---:|
| 0 | 0 | 1974 | 0 |
| 1,000 | 1,000 | 1977 | 1 |
| 5,000 | 5,000 | 1991 | 4 |
| 10,000 | 10,000 | 2008 | 15 |
| 14,000 | 14,000 | 2022 | 21 |
| 15,000 | 15,000 | 2026 | 21 |
| 16,000 | 15,000 | 2026 | 21 |

## 실행 명령

```text
playwright screenshot --wait-for-timeout 16000 --viewport-size='1080,1920' file:///E:/ax/PRJs/gpt56-scaling/runs/test3b/terra_max/index.html final.png
```

`final.png`은 검증 과정의 임시 산출물이며, 최종 배포에 필요한 것은 `index.html`뿐이다.
