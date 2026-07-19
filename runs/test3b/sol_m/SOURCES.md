# SOURCES

## 범위와 기준

- 최종 포함 노선: **24개** (서울 1~9호선 + 수도권 주요 광역·도시철도·경전철 15개)
- 시간 범위: **1974–2026**
- `개통 연도`는 해당 노선 또는 현재 노선의 모체가 된 수도권 전철 운행계통의 **최초 여객 영업 개시 연도**다.
  - 수인·분당선은 현재 명칭(2020)보다 앞선 분당선 최초 개통(1994)을 사용했다.
  - 경의·중앙선은 통합 명칭(2014)보다 앞선 중앙선 수도권 전철 운행 개시(2005)를 사용했다.
- 2026은 타임라인의 최종 기준 연도다. 개통이 확정되지 않은 2025–2026 계획선은 넣지 않았다. 마지막 신규 노선은 2024년 GTX-A의 실제 개통 구간이다.
- 역명 라벨은 전체 역명이 아니라 모션그래픽 가독성을 위한 주요 환승역 9곳만 표시한다. 작은 노선색 마커는 원본 벡터 노선도에 들어 있는 역 위치를 이용한다.

## 1. 노선 위치·연결 구조·역 노드

### Wikimedia Commons 수도권 전철 네트워크 맵

- 파일 설명: https://commons.wikimedia.org/wiki/File:Seoul_Metropolitan_Subway_network_map.svg
- 원본 SVG: https://upload.wikimedia.org/wikipedia/commons/e/e6/Seoul_Metropolitan_Subway_network_map.svg
- 저자: Wikimedia Commons 사용자 `Satellizer`
- 현재 사용한 리비전 시각: **2023-09-09T14:42:17Z** (MediaWiki API의 `imageinfo.timestamp`로 확인)
- 라이선스: **CC BY-SA 4.0** — https://creativecommons.org/licenses/by-sa/4.0/

가공 방법:

1. 원본 SVG에서 노선별 `stroke` 색과 범례를 대조해 실제 운행 노선의 `<path>`, `<line>`, `<polyline>`만 추출했다.
2. 같은 노선색의 `<circle>`/`<ellipse>`를 역 노드로 추출했다.
3. 원본의 배경·행정경계·범례·전체 역명·미개통 계획선은 제거했다.
4. 서울 중심부가 세로 화면에서 읽히도록 원본 좌표계의 `viewBox="1200 430 5900 5550"` 구간을 선택하고 1080×1920 스테이지의 지도 영역에 비등방 스케일링했다. 따라서 결과는 지리 지도라기보다 **연결 구조를 보존한 개략도**다.
5. 신림선은 원본 SVG에 이미 들어 있는 신림선 경로를 2022년에 활성화했다.
6. GTX-A는 같은 SVG의 계획선 도형 중 실제 2024년에 영업을 시작한 두 구간(운정중앙–서울역 축, 수서–동탄 축)만 분리해 보라색으로 활성화했다. 미개통 중앙 연결부는 제외했다.
7. 주요 환승역 9곳(서울역, 시청, 종로3가, 왕십리, 건대입구, 강남, 고속터미널, 여의도, 김포공항)은 원본 SVG의 역명/노드 좌표에 별도 흰색 이중 원 마커와 한국어 라벨을 얹었다.

참고 조사(최종 도형에는 직접 병합하지 않음):

- OpenStreetMap Nominatim에서 신림선·GTX-A 선형 객체의 존재를 교차 확인했다.
  - https://nominatim.openstreetmap.org/
  - OSM 저작권/라이선스: https://www.openstreetmap.org/copyright
- 서울 열린데이터광장 `subwayStationMaster` 샘플 API로 역 마스터가 `역명·노선·위도·경도` 필드를 제공함을 확인했다. 샘플 키는 5건 제한이라 최종 전체 선형에는 사용하지 않았다.
  - http://openapi.seoul.go.kr:8088/sample/json/subwayStationMaster/1/5/
  - https://data.seoul.go.kr/

## 2. 개통 연도와 노선 색상

서울 1~9호선 색은 서울교통공사 사이버스테이션/노선도의 표준색을 사용했다.

- 서울교통공사 사이버스테이션: https://www.seoulmetro.co.kr/kr/cyberStation.do
- 수도권 전철 개요 및 노선 목록: https://en.wikipedia.org/wiki/Seoul_Metropolitan_Subway

광역노선 색은 각 노선 문서의 노선색과 Commons SVG 범례를 교차 대조해 웹용 HEX로 정규화했다. 개통 연도는 아래 각 노선 문서의 `Opened`/역사 절을 기준으로 했다.

| 노선 | 사용 연도 | HEX | 연도 근거 |
|---|---:|---:|---|
| 1호선 | 1974 | `#0052A4` | https://en.wikipedia.org/wiki/Seoul_Subway_Line_1 |
| 2호선 | 1980 | `#00A84D` | https://en.wikipedia.org/wiki/Seoul_Subway_Line_2 |
| 3호선 | 1985 | `#EF7C1C` | https://en.wikipedia.org/wiki/Seoul_Subway_Line_3 |
| 4호선 | 1985 | `#00A5DE` | https://en.wikipedia.org/wiki/Seoul_Subway_Line_4 |
| 수인·분당선 | 1994 | `#F5A200` | https://en.wikipedia.org/wiki/Suin%E2%80%93Bundang_Line |
| 5호선 | 1995 | `#996CAC` | https://en.wikipedia.org/wiki/Seoul_Subway_Line_5 |
| 7호선 | 1996 | `#747F00` | https://en.wikipedia.org/wiki/Seoul_Subway_Line_7 |
| 8호선 | 1996 | `#E6186C` | https://en.wikipedia.org/wiki/Seoul_Subway_Line_8 |
| 인천 1호선 | 1999 | `#7CA8D5` | https://en.wikipedia.org/wiki/Incheon_Subway_Line_1 |
| 6호선 | 2000 | `#CD7C2F` | https://en.wikipedia.org/wiki/Seoul_Subway_Line_6 |
| 경의·중앙선 | 2005 | `#77C4A3` | https://en.wikipedia.org/wiki/Gyeongui%E2%80%93Jungang_Line |
| 공항철도 | 2007 | `#0090D2` | https://en.wikipedia.org/wiki/AREX |
| 9호선 | 2009 | `#BDB092` | https://en.wikipedia.org/wiki/Seoul_Subway_Line_9 |
| 경춘선 | 2010 | `#0C8E72` | https://en.wikipedia.org/wiki/Gyeongchun_Line |
| 신분당선 | 2011 | `#D4003B` | https://en.wikipedia.org/wiki/Shinbundang_Line |
| 의정부경전철 | 2012 | `#FDA600` | https://en.wikipedia.org/wiki/U_Line |
| 에버라인 | 2013 | `#6FB245` | https://en.wikipedia.org/wiki/EverLine |
| 경강선 | 2016 | `#0054A6` | https://en.wikipedia.org/wiki/Gyeonggang_Line |
| 인천 2호선 | 2016 | `#ED8B00` | https://en.wikipedia.org/wiki/Incheon_Subway_Line_2 |
| 우이신설선 | 2017 | `#B7C452` | https://en.wikipedia.org/wiki/Ui_LRT |
| 서해선 | 2018 | `#8FC31F` | https://en.wikipedia.org/wiki/Seohae_Line |
| 김포골드라인 | 2019 | `#A17800` | https://en.wikipedia.org/wiki/Gimpo_Goldline |
| 신림선 | 2022 | `#6789CA` | https://en.wikipedia.org/wiki/Sillim_Line |
| GTX-A | 2024 | `#9A6292` | https://en.wikipedia.org/wiki/GTX-A |

## 3. 내장 폰트

- Pretendard v1.3.9 Regular/Bold WOFF2 subset
- 저장소: https://github.com/orioncactus/pretendard/tree/v1.3.9
- 사용 파일:
  - `packages/pretendard/dist/web/static/woff2-subset/Pretendard-Regular.subset.woff2`
  - `packages/pretendard/dist/web/static/woff2-subset/Pretendard-Bold.subset.woff2`
- 라이선스: SIL Open Font License 1.1 — https://github.com/orioncactus/pretendard/blob/v1.3.9/LICENSE
- 두 WOFF2를 Base64 data URL로 변환해 `index.html`의 `@font-face` 안에 직접 내장했다. 실행 시 폰트 요청은 발생하지 않는다.

## 4. 산출물 내부 데이터 요약

- 노선: 24
- 최초 개통 연도 범위: 1974–2024
- 표시 타임라인 범위: 1974–2026
- 주요 환승역 라벨: 9
- 외부 이미지: 없음
- 외부 스크립트/CSS: 없음
- 런타임 네트워크 의존성: 없음
