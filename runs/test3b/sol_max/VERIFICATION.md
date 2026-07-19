# VERIFICATION

검증 시각: 2026-07-19 18:43 KST  
대상: `file:///E:/ax/PRJs/gpt56-scaling/runs/test3b/sol_max/index.html`  
브라우저: Playwright 1.58.0 / Chromium headless  
검증 스크립트: `verify_browser.py`  
원시 결과: `verification_results.json`

## 최종 판정

**전체 달성 기준: PASS**

| 기준 | 결과 | 실제 확인값 |
|---|---|---|
| 단일 실행 파일 | PASS | 실행에 필요한 HTML/CSS/JS/데이터/폰트가 `index.html` 하나에 포함됨 |
| 외부 실행 요청 없음 | PASS | HTTP/HTTPS 런타임 요청 0건; 전체 요청 1건은 `file://.../index.html` 문서 자체 |
| 콘솔 오류 0건 | PASS | console error 0, page error 0, failed request 0 |
| 1080×1920 고정 스테이지 | PASS | Canvas `[1080,1920]` |
| 스크롤 없음 | PASS | document scroll `[1080,1920]` = viewport `[1080,1920]`, body overflow `hidden` |
| 오디오 없음 | PASS | audio/media 요소 및 오디오 코드 없음 |
| requestAnimationFrame 기반 | PASS | 시작·진행 루프가 `requestAnimationFrame(frame)` 사용 |
| 15.0초 완결 | PASS | 실제 rAF 계측에서 `{t:15, year:2026, lines_shown:24}` |
| 마지막 약 1초 완성 화면 | PASS | t=14.016에 24/24, t=15.000에도 24/24 |
| 15초 이후 최종 화면 유지 | PASS | 0.7초 후에도 `t=15`; Canvas PNG 바이트 완전 동일 |
| 매 프레임 `window.__mg` 갱신 | PASS | render가 매 rAF에서 `{t, year, lines_shown}`를 재할당 |
| 시작부터 전체 흐린 가이드 | PASS | 활성 노선 렌더 전에 24개 전체 선분을 저명도 guide로 그림 |
| 연도에 따른 채움 | PASS | 노선별 개통 연도를 1974–2026의 14초 성장 구간에 매핑하고 선분 sweep 적용 |
| 환승역 구분 | PASS | 일반역은 작은 색 점, 환승역은 검은 내부/흰색 외곽 링 |
| 주요 역 라벨 | PASS | 김포공항·홍대입구·서울역·왕십리·신도림·강남·잠실·수서가 해당 노선 등장 뒤 표시 |
| 최종 시각 QA | PASS | 1080×1920 캡처 확인; 텍스트 잘림 없음, 주요 라벨 수를 8개로 조정해 중앙부 중첩 완화, 범례 정상 |

## 실제 rAF `window.__mg` 시퀀스

Playwright가 애니메이션을 실제 시간으로 실행하고 각 목표 초를 통과한 첫 프레임의 값을 읽었다. 브라우저 프레임 경계 때문에 일부 표본은 목표보다 0.016–0.033초 뒤다.

| 표본 | `t` | `year` | `lines_shown` |
|---:|---:|---:|---:|
| 0 | 0.133 | 1974 | 0 |
| 1 | 1.000 | 1977 | 1 |
| 2 | 2.000 | 1981 | 1 |
| 3 | 3.000 | 1985 | 2 |
| 4 | 4.000 | 1988 | 4 |
| 5 | 5.000 | 1992 | 4 |
| 6 | 6.000 | 1996 | 5 |
| 7 | 7.000 | 1999 | 8 |
| 8 | 8.000 | 2003 | 10 |
| 9 | 9.000 | 2007 | 10 |
| 10 | 10.016 | 2011 | 13 |
| 11 | 11.016 | 2014 | 16 |
| 12 | 12.033 | 2018 | 19 |
| 13 | 13.016 | 2022 | 22 |
| 14 | 14.016 | 2026 | 24 |
| 15 | **15.000** | **2026** | **24** |
| +0.7초 | **15.000** | **2026** | **24** |

`lines_shown`은 그리기 전환을 끝낸 노선 수다. 등장 중인 노선은 완료 임계값에 도달한 다음 카운트된다.

## 정지 화면 동일성

- t=15.0 캡처와 0.7초 후 캡처: **바이트 단위 동일**
- 최종 Canvas PNG SHA-256: `3c0ba490c9d85559571ff62dea383fba5549eddfb9e120887b7c461493438fb5`
- 최종 프레임 PNG 크기: 376,256 bytes
- 시각 점검용 캡처: `final.png`

## 파일 무결성

- `index.html` 크기: 1,542,942 bytes
- `index.html` SHA-256: `bff528a5ff84f819565e224a9e63af64c7f6d720835ccf566c30ea951ef308dd`
- HTML 문자열 검사:
  - `http://`: 0
  - `https://`: 0
  - 외부 `src="..."`: 0
  - 외부 `href="..."`: 0
- 폰트: WOFF2 400/700 두 개를 data URI로 내장

## 재현 명령

현재 폴더에서:

```bash
python verify_browser.py
```

브라우저에서 결과를 보려면 `index.html`을 직접 열면 된다. 별도 서버나 네트워크 연결은 필요 없다.
