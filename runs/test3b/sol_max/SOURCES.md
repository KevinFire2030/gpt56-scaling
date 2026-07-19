# SOURCES

조사·가공 기준일: 2026-07-19 (KST)

## 1. 결과 데이터 범위

- 화면 연도 범위: **1974–2026**
- 표시 노선 수: **24개**
- 노선 최초 개통 연도 범위: **1974–2024** (2025–2026에는 이 선정 범위에서 새 노선을 추가하지 않고 2026 완성 화면으로 진행)
- 기본 역 그래프: 원본 631개 역 레코드 중 선택 노선에 해당하는 **626개 역 레코드** 내장
- 추가 형상: 신림선 11개 역, GTX-A 2개 분리 운행 구간 9개 역
- 범위: 서울 1–9호선 전부 + 수도권의 주요 광역/도시철도(수인·분당, 인천 1·2, 공항철도, 경의·중앙, 경춘, 신분당, 의정부, 용인, 경강, 우이신설, 서해, 김포골드, 신림, GTX-A)

> 이 작품은 열차 운행용 도면이 아니라 15초 모션그래픽이다. 좌표는 실제 위·경도와 실제 인접역 관계를 1080×1920 화면에 선형 투영한 지리 기반 개략도다. 2021 기본 그래프 뒤에 개통한 신림선과 GTX-A 운행 구간은 별도로 보강했다. 모든 세부 연장·분기 이력을 구간별로 재연하는 대신, 각 선정 노선의 수도권 전철 여객 영업 시작 연도에 현재 선정 형상을 등장시키는 방식을 사용했다.

## 2. 역 위치와 연결 구조

### Korea-Subway 공개 그래프

- 저장소: https://github.com/iml1111/Korea-Subway
- 사용 파일: `dataset/capitalStations.json`
- 고정 커밋: `c75037129fa79ad121b8987d901765b0da09ce57`
- 저장소 표기 데이터 갱신일: 2021-05-12
- 라이선스: MIT, Copyright (c) 2021 IML
- 사용 필드: 역명, 소속 노선, 위도, 경도, 인접역 목록
- 가공:
  1. 아래 22개 기본 노선 키만 선택했다.
  2. 한 역과 인접역이 같은 노선 키를 공유할 때만 선분을 생성했다.
  3. 동일 선분의 양방향 중복을 제거했다.
  4. 동명이역 후보는 같은 노선을 공유하는 후보 중 지리적으로 가장 가까운 역을 선택했다.
  5. 위·경도를 고정 지도 박스에 선형 투영했다. 연결 순서나 역명은 새로 만들지 않았다.

### OpenStreetMap / Nominatim 보강

- 검색 API: https://nominatim.openstreetmap.org/search
- 데이터 저작권: OpenStreetMap contributors, ODbL 1.0 — https://www.openstreetmap.org/copyright
- 로컬 조사 원문: `nominatim_results.json`
- 용도: 2022년 개통 신림선과 2024년 개통 GTX-A 운행 구간의 역 좌표 확인
- GTX-A는 2026-07-19 현재 연결되지 않은 **운정중앙–서울역**, **수서–동탄** 두 운행 구간을 서로 잇지 않고 따로 그렸다. 삼성역 또는 미개통 중앙 연결부는 표시하지 않았다.
- Nominatim이 반환하지 않은 신림선 `서울지방병무청`, `관악산(서울대)` 두 점은 실제 노선 순서를 유지하면서 인접 OSM 역 좌표 사이에 시각용으로 보간했다. 이 두 좌표는 측량 좌표로 사용하지 않는다.

### 최신 역명 목록 교차 확인

- 저장소: https://github.com/dart-bird/korea-subway-stations
- 고정 커밋: `64536f31bf1ebd9e8b28847f4d720607bf487513`
- 데이터 파일: `seoul_stations.json`
- 용도: 수도권 노선/역명 목록 교차 확인. 좌표·형상 생성에는 사용하지 않았다.

## 3. 개통 연도와 노선 색상

개통 연도는 각 노선 문서의 최초 여객 영업 시작을 사용했다. 합쳐지거나 이름이 바뀐 노선은 괄호의 기준을 적용했다. 색상은 Wikipedia의 수도권 전철 `rcr` 노선색 템플릿 또는 각 노선 문서의 명시 색상 값을 사용했다.

| 표시 노선 | 연도 | 색상 | 기준/출처 |
|---|---:|---:|---|
| 1호선 | 1974 | `#0052A4` | https://en.wikipedia.org/wiki/Seoul_Subway_Line_1 |
| 2호선 | 1980 | `#00A84D` | https://en.wikipedia.org/wiki/Seoul_Subway_Line_2 |
| 3호선 | 1985 | `#EF7C1C` | https://en.wikipedia.org/wiki/Seoul_Subway_Line_3 |
| 4호선 | 1985 | `#00A4E3` | https://en.wikipedia.org/wiki/Seoul_Subway_Line_4 |
| 분당선 → 수인·분당선 | 1994 | `#FABE00` | 분당선 최초 개통 기준; 통합 운행 2020 — https://en.wikipedia.org/wiki/Suin%E2%80%93Bundang_Line |
| 5호선 | 1995 | `#996CAC` | https://en.wikipedia.org/wiki/Seoul_Subway_Line_5 |
| 7호선 | 1996 | `#747F00` | https://en.wikipedia.org/wiki/Seoul_Subway_Line_7 |
| 8호선 | 1996 | `#E6186C` | https://en.wikipedia.org/wiki/Seoul_Subway_Line_8 |
| 인천 1호선 | 1999 | `#7CA8D5` | https://en.wikipedia.org/wiki/Incheon_Subway_Line_1 |
| 6호선 | 2000 | `#CD7C2F` | https://en.wikipedia.org/wiki/Seoul_Subway_Line_6 |
| 공항철도 | 2007 | `#0090D2` | https://en.wikipedia.org/wiki/AREX |
| 9호선 | 2009 | `#BDB092` | https://en.wikipedia.org/wiki/Seoul_Subway_Line_9 |
| 경의선 전철 → 경의·중앙선 | 2009 | `#77C4A3` | 경의선 수도권 전철 시작 기준; 통합 운행 2014 — https://en.wikipedia.org/wiki/Gyeongui%E2%80%93Jungang_Line |
| 경춘선 전철 | 2010 | `#0C8E72` | 복선전철 수도권 전철 운행 시작 기준 — https://en.wikipedia.org/wiki/Gyeongchun_Line |
| 신분당선 | 2011 | `#D4003B` | https://en.wikipedia.org/wiki/Shinbundang_Line |
| 의정부 경전철 | 2012 | `#FDA600` | https://en.wikipedia.org/wiki/Uijeongbu_LRT |
| 용인 에버라인 | 2013 | `#6FB245` | https://en.wikipedia.org/wiki/EverLine |
| 인천 2호선 | 2016 | `#ED8B00` | https://en.wikipedia.org/wiki/Incheon_Subway_Line_2 |
| 경강선 | 2016 | `#003DA5` | 수도권 판교–여주 구간 기준 — https://en.wikipedia.org/wiki/Gyeonggang_Line |
| 우이신설선 | 2017 | `#B7C452` | https://en.wikipedia.org/wiki/Ui_LRT |
| 서해선 | 2018 | `#8FC31F` | 소사–원시 첫 구간 기준 — https://en.wikipedia.org/wiki/Seohae_Line |
| 김포골드라인 | 2019 | `#A17800` | https://en.wikipedia.org/wiki/Gimpo_Goldline |
| 신림선 | 2022 | `#6789CA` | 문서 명시 색상 및 2022-05-28 개통 — https://en.wikipedia.org/wiki/Sillim_Line |
| GTX-A | 2024 | `#9A6292` | 최초 수서–동탄 구간 개통 기준 — https://en.wikipedia.org/wiki/Great_Train_eXpress |

Wikipedia 원문은 MediaWiki API `action=parse&prop=wikitext`로 내려받아 `wiki_pages.json`에 보존했다. 1–9호선 등 템플릿 색상은 `action=expandtemplates`로 16진수 값을 확인했다.

## 4. 오픈소스 노선도 교차 확인

- 프로젝트: https://github.com/Sinseiki/opensource-seoul-subway-map
- 고정 커밋: `06e3184f6951895919f0156cc08b396e84ecf429`
- 파일: `mapimage.svg`
- 라이선스: MIT, Copyright (c) 2020 Sinseiki
- 용도: 노선 색상 팔레트와 환승 구조를 시각적으로 교차 확인. SVG 자체를 최종 파일에 복사하지 않았고, 완성 화면은 Canvas로 새로 렌더링했다.

## 5. 내장 폰트

- 패키지: `@fontsource/noto-sans-kr` 5.2.6
- 배포: https://www.jsdelivr.com/package/npm/@fontsource/noto-sans-kr
- 사용 파일: Korean 400/700 WOFF2
- 라이선스: SIL Open Font License 1.1
- 가공: WOFF2 두 파일을 Base64 data URI로 `index.html`에 직접 내장했다. 실행 시 폰트 요청은 발생하지 않는다.

## 6. 내장 방식

- 역/노선 데이터: JavaScript 객체로 `index.html` 내부 삽입
- 폰트: Base64 WOFF2 data URI
- 이미지: 사용하지 않음(Canvas가 매 프레임 직접 그림)
- 오디오: 없음
- 외부 URL 참조: 없음 (`http://`, `https://`, 외부 `src`/`href` 0개)
