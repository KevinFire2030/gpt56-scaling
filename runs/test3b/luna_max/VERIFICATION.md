# VERIFICATION.md

검증 일시: 2026-07-19 (로컬 헤드리스 실행)
검증 대상: `index.html`
브라우저: Playwright Chromium headless, viewport 1080×1920

## 결과 요약

- [통과] `index.html`을 `file://`로 직접 열림
- [통과] 브라우저 콘솔 에러 0건
- [통과] 페이지 런타임 네트워크 요청 0건(문서 자체의 `file://` 로드 1건만 관측)
- [통과] `requestAnimationFrame` 기반 애니메이션 사용
- [통과] 고정 1080×1920 스테이지, `html/body` 스크롤 숨김
- [통과] 애니메이션 종료 후 `window.__mg.t`가 15로 고정되고 최종 화면 유지
- [통과] 최종 계측값 `year=2026`, `lines_shown` 26개
- [통과] 최종 프레임 스크린샷으로 시각 점검 완료: 제목·연도·전체 노선·환승 마커·역 라벨·범례가 화면 안에 표시됨

## 실제 콘솔/요청 결과

Playwright 이벤트 수집 결과:

```text
CONSOLE []
PAGEERROR []
REQUESTS ['file:///E:/ax/PRJs/gpt56-scaling/runs/test3b/luna_max/index.html']
```

`REQUESTS`의 단일 항목은 테스트 대상 HTML 문서의 로컬 `file://` 로드이며, HTTP/HTTPS 외부 요청은 0건입니다.

## 실제 `window.__mg` 시퀀스

아래 값은 페이지를 연 뒤 실제 경과 시간을 기준으로 Playwright에서 읽은 값입니다. 프레임 스케줄링에 따라 관측 시각은 몇 ms 변동할 수 있습니다.

```text
경과 0 ms      -> {"t":0,      "year":1974, "lines_shown":[]}
경과 1000 ms   -> {"t":1.033,  "year":1978, "lines_shown":["1"]}
경과 3000 ms   -> {"t":3.05,   "year":1985, "lines_shown":["1","2","3","4"]}
경과 6000 ms   -> {"t":6.05,   "year":1996, "lines_shown":["1","2","3","4","5","B","7","8"]}
경과 9000 ms   -> {"t":9.066,  "year":2008, "lines_shown":["1","2","3","4","5","B","7","8","6","IC1","J","AREX"]}
경과 12000 ms  -> {"t":12.066, "year":2019, "lines_shown":["1","2","3","4","5","B","7","8","6","IC1","J","AREX","9","GJ","GC","SB","UIJ","SUIN","EV","G","IC2","UIS","SEOHAE"]}
경과 14000 ms  -> {"t":14.083, "year":2026, "lines_shown":["1","2","3","4","5","B","7","8","6","IC1","J","AREX","9","GJ","GC","SB","UIJ","SUIN","EV","G","IC2","UIS","SEOHAE","GIMPO","SILLIM","GTXA"]}
경과 15000 ms  -> {"t":15,     "year":2026, "lines_shown":["1","2","3","4","5","B","7","8","6","IC1","J","AREX","9","GJ","GC","SB","UIJ","SUIN","EV","G","IC2","UIS","SEOHAE","GIMPO","SILLIM","GTXA"]}
경과 16000 ms  -> {"t":15,     "year":2026, "lines_shown":["1","2","3","4","5","B","7","8","6","IC1","J","AREX","9","GJ","GC","SB","UIJ","SUIN","EV","G","IC2","UIS","SEOHAE","GIMPO","SILLIM","GTXA"]}
```

14초 관측은 프레임 타이밍 때문에 14.083초였지만 이미 전체 노선이 완성되어 있었고, 15초 및 16초 값이 동일하여 종료 후 정지 상태를 확인했습니다.

## 추가 정적 확인

- `index.html` 내부에 `http://`, `https://`, 외부 폰트 URL, 이미지 URL, 오디오 URL 없음
- CSS·JavaScript·노선 데이터·폰트 지정이 모두 단일 HTML 안에 있음
- 캔버스 선언: `width="1080" height="1920"`
- 애니메이션 루프: `requestAnimationFrame(frame)`
- 종료 조건: `t=Math.min(duration,(now-t0)/1000)`, `if(t<duration)requestAnimationFrame(frame)`
