# VERIFICATION

검증일: 2026-07-19
검증 환경: Playwright Chromium Headless 145.0.7632.6, 1080×1920 viewport, deviceScaleFactor 1
대상: `file:///E:/ax/PRJs/gpt56-scaling/runs/test3b/sol_u/index.html`

## 결과 요약

| 달성 기준 | 결과 | 실제 확인값 |
|---|---|---|
| 단일 실행 파일 | PASS | 런타임은 `index.html` 한 파일만 로드 |
| 외부 리소스 요청 없음 | PASS | HTTP/HTTPS 요청 0건; 전체 요청은 로컬 `index.html` 1건 |
| 콘솔 에러 0건 | PASS | console error 0, page error 0 |
| 1080×1920 고정 스테이지 | PASS | canvas `[1080,1920]`, viewport `[1080,1920]` |
| 스크롤 없음 | PASS | document scroll 크기 `[1080,1920]` |
| 폰트 내장/로드 | PASS | `document.fonts.status === "loaded"`; 외부 `src`/`href` 0건 |
| requestAnimationFrame 기반 | PASS | 소스에서 rAF 시작/반복 호출 확인 |
| 시작부터 전체 흐린 가이드 | PASS | `guide()`가 24개 전체 노선을 매 프레임 활성 노선보다 먼저 그림 |
| 연도에 따라 노선 성장 | PASS | 아래 `window.__mg` 시퀀스에서 연도와 노선 수 증가 확인 |
| 일반역/환승역 구분 | PASS | 일반역은 작은 채움점, 환승역은 흰 외곽선+암색 중심 원 |
| 주요 역 라벨 | PASS | 서울역·종로3가·홍대입구·왕십리·강남·잠실·김포공항 7개 |
| 14.0초부터 최종 화면 | PASS | 14.0328초 샘플에서 2026/24개, 이후 최종 상태 유지 |
| 정확히 15.0초 완결/정지 | PASS | 15.0초에서 `{t:15, year:2026, lines_shown:24}` |
| 15초 이후 정지 화면 유지 | PASS | 1.3초 추가 대기 후 계측값 완전 동일 |
| 오디오 없음 | PASS | audio/video 요소 및 Web Audio 사용 없음 |
| 시각 검수 | PASS | 최종 PNG에서 텍스트 잘림 없음, 라벨 간 직접 겹침 없음, 9:16 레이아웃 안정 |

## 실제 `window.__mg` 시퀀스

Playwright가 실제 rAF 실행 중 목표 시점을 통과한 첫 프레임에서 읽은 값이다. 프레임 경계 때문에 중간 시점은 약 0~33ms 늦을 수 있으며, 최종값은 코드에서 15.0초로 고정된다.

```json
[
  {"target": 0,  "t": 0.0666, "year": 1974, "lines_shown": 1},
  {"target": 1,  "t": 1.0,    "year": 1977, "lines_shown": 1},
  {"target": 3,  "t": 3.0166, "year": 1985, "lines_shown": 4},
  {"target": 5,  "t": 5.0165, "year": 1992, "lines_shown": 4},
  {"target": 7,  "t": 7.033,  "year": 2000, "lines_shown": 10},
  {"target": 9,  "t": 9.0163, "year": 2007, "lines_shown": 12},
  {"target": 11, "t": 11.0162,"year": 2014, "lines_shown": 17},
  {"target": 13, "t": 13.0161,"year": 2022, "lines_shown": 23},
  {"target": 14, "t": 14.0328,"year": 2026, "lines_shown": 24},
  {"target": 15, "t": 15.0,   "year": 2026, "lines_shown": 24}
]
```

15초 정지 검증:

```json
{
  "before": {"t": 15, "year": 2026, "lines_shown": 24},
  "after_1_3s": {"t": 15, "year": 2026, "lines_shown": 24}
}
```

## 네트워크·콘솔 원시 요약

```json
{
  "console_errors": [],
  "page_errors": [],
  "http_requests": [],
  "all_requests": ["file:///E:/ax/PRJs/gpt56-scaling/runs/test3b/sol_u/index.html"],
  "external_src_or_href": [],
  "fontStatus": "loaded"
}
```

## 파일 무결성

- `index.html` 크기: 41,834 bytes
- SHA-256: `5bdbbff1dcc754ae8532f0eb93e74e0a948edb85d4db48ffb7035dcecea0aacb`
- 소스 정적 스캔: `http://`/`https://` 토큰 0개, `requestAnimationFrame` 2회, `window.__mg` 할당 지점 2개(초기값 + 매 프레임 갱신).

## 검증 절차

1. Playwright Chromium을 1080×1920로 열었다.
2. `file://`로 `index.html`을 직접 로드했다.
3. `console`, `pageerror`, `request` 이벤트를 수집했다.
4. rAF 실행 중 `window.__mg.t`가 각 목표 시점을 통과할 때 값을 기록했다.
5. 15초 값 기록 후 1.3초 더 기다려 정지 상태를 비교했다.
6. 최종 프레임을 PNG로 캡처해 텍스트 잘림, 라벨 중첩, 맵/패널/타임라인 배치를 시각 검수했다.
