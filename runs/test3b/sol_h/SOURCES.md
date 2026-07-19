# SOURCES.md

## 범위와 기준

- 조사·가공 시각: 2026-07-19 (KST)
- 애니메이션 시간 범위: 1974–2026
- 포함 노선: 서울 1–9호선과 수도권 주요 광역/경전철 10개, 총 19개 노선
- 최신 개통 이정표는 2024년 GTX-A입니다. 2025–2026에 이 작업의 선정 범위 안에서 새 노선을 임의로 추가하지 않았으며, 2026은 최신 공개 지리 데이터를 보여 주는 종료 연도입니다.
- “개통 연도”는 현재 화면에 표시하는 **노선 정체성의 최초 여객 영업 연도**입니다. 통합 노선은 통합 명칭의 서비스 개시 연도(경의·중앙 2014, 수인·분당 2020)를 사용했습니다. 경춘선은 수도권 전철 서비스 개시(2010)를 사용했습니다.

## 노선·역 위치·연결 구조

### OpenStreetMap / Overpass API

- OpenStreetMap: https://www.openstreetmap.org/
- 저작권·ODbL 1.0: https://www.openstreetmap.org/copyright
- Overpass API: https://overpass-api.de/api/interpreter
- 원자료 시각: `timestamp_osm_base = 2026-07-19T09:35:00Z`
- 사용 쿼리 형태:

```overpass
[out:json][timeout:300];
rel(id:443803,2404374,2718884,2718887,2718888,2718901,
  2911378,3012654,4727111,4729405,4729407,4744337,4748705,
  5993211,6060963,6462562,8656357,8667955,8691809,8692707,
  8692927,12497485,12746493,14191876,16244687,17413294,18828088);
out geom;
```

- 선택 기준: 각 노선의 완행 방향 관계 중 최신 종점과 지선을 덮는 관계를 선택했습니다. 반대 방향의 같은 선형은 중복 렌더링을 피하려고 제외했습니다.
- 색상: 위 OSM route relation의 `colour` 태그를 그대로 사용했습니다. 우이신설선만 아래 Wikimedia 네트워크 맵의 색을 참고했습니다.
- 역: 선택한 route relation의 `role=stop` 노드 723개를 조회하고, 노드 태그의 한국어/기본 역명으로 플랫폼 중복을 합쳤습니다.
- 연결/환승: 같은 역명이 둘 이상의 선정 노선에 속하면 환승역으로 분류했습니다. 결과는 이름 기준 역 555개, 환승역 96개입니다.
- 선형 단순화: Douglas–Peucker 허용오차 0.00035도. 종점과 분기별 path는 보존했습니다.
- 화면 투영: 경도/위도를 1080×1920 무대의 지도 영역에 가로·세로 독립 선형 스케일링했습니다. 따라서 거리·각도 보존 지도라기보다 지리형 모션그래픽입니다.

### Wikimedia Commons 공개 네트워크 맵

- 파일 페이지: https://commons.wikimedia.org/wiki/File:Seoul_Metropolitan_Subway_network_map.svg
- 원본 SVG: https://upload.wikimedia.org/wikipedia/commons/e/e6/Seoul_Metropolitan_Subway_network_map.svg
- 파일 표기 버전: 3.1, “Correct as of 26 August 2023”
- 라이선스: 파일 페이지의 CC BY-SA 조건 적용
- 사용 방식: OSM 관계 검색에서 빠진 우이신설선의 실제 13개 역 순서와 연결 회랑, 색상을 교차 확인했습니다. 우이신설선 역들은 실제 순서를 유지한 등간격 스키매틱 점으로 보강했고, 신설동·보문·성신여대입구의 기존 OSM 환승 좌표는 유지했습니다. SVG 자체나 이미지는 최종 HTML에 복사하지 않았습니다.

## 개통 연도와 표시 색

아래 링크의 노선 역사/개통 정보를 교차 확인했습니다. 색은 화면에 실제 사용한 값입니다.

| 표시 노선 | 연도 | 색 | 개통 정보 출처 |
|---|---:|---|---|
| 1호선 | 1974 | `#004A85` | https://en.wikipedia.org/wiki/Seoul_Subway_Line_1 |
| 2호선 | 1980 | `#00A23F` | https://en.wikipedia.org/wiki/Seoul_Subway_Line_2 |
| 3호선 | 1985 | `#ED6C00` | https://en.wikipedia.org/wiki/Seoul_Subway_Line_3 |
| 4호선 | 1985 | `#009BCE` | https://en.wikipedia.org/wiki/Seoul_Subway_Line_4 |
| 5호선 | 1995 | `#794698` | https://en.wikipedia.org/wiki/Seoul_Subway_Line_5 |
| 7호선 | 1996 | `#6E7E31` | https://en.wikipedia.org/wiki/Seoul_Subway_Line_7 |
| 8호선 | 1996 | `#D11D70` | https://en.wikipedia.org/wiki/Seoul_Subway_Line_8 |
| 6호선 | 2000 | `#7C4932` | https://en.wikipedia.org/wiki/Seoul_Subway_Line_6 |
| 공항철도 | 2007 | `#0079AC` | https://en.wikipedia.org/wiki/AREX |
| 9호선 | 2009 | `#A49D87` | https://en.wikipedia.org/wiki/Seoul_Subway_Line_9 |
| 경춘선(수도권 전철) | 2010 | `#007A62` | https://en.wikipedia.org/wiki/Gyeongchun_Line |
| 신분당선 | 2011 | `#B81B30` | https://en.wikipedia.org/wiki/Shinbundang_Line |
| 경의·중앙선 | 2014 | `#6AC2B3` | https://en.wikipedia.org/wiki/Gyeongui%E2%80%93Jungang_Line |
| 경강선 | 2016 | `#0B318F` | https://en.wikipedia.org/wiki/Gyeonggang_Line |
| 우이신설선 | 2017 | `#B7C452` | https://en.wikipedia.org/wiki/Ui_LRT |
| 서해선 | 2018 | `#5EAC41` | https://en.wikipedia.org/wiki/Seohae_Line |
| 수인·분당선 | 2020 | `#ECA300` | https://en.wikipedia.org/wiki/Suin%E2%80%93Bundang_Line |
| 신림선 | 2022 | `#6789CA` | https://en.wikipedia.org/wiki/Sillim_Line |
| GTX-A | 2024 | `#AB087D` | https://en.wikipedia.org/wiki/GTX-A |

## 주요 역 라벨

화면 라벨은 서울역(1974), 잠실(1980), 강남(1982), 왕십리(1983), 여의도(1996), 김포공항(1996)입니다. 위치는 OSM stop 노드 좌표를 사용하고, 표기 연도는 각 역의 최초 서울 도시철도 영업 연도를 사용했습니다. 철도역 자체의 더 오래된 국철 개업과 혼동하지 않도록 “도시철도/지하철 개통” 기준으로만 등장시켰습니다.

## 글꼴

- Noto Sans KR variable font: https://github.com/google/fonts/tree/main/ofl/notosanskr
- 라이선스: SIL Open Font License 1.1
- 가공: 화면에서 사용하는 문자만 WOFF2로 서브셋(48,780바이트)하여 `index.html`의 `@font-face` data URI에 내장했습니다.

## 최종 데이터 요약

- 노선 수: 19
- 애니메이션 연도 범위: 1974–2026
- 실제 노선 개통 이정표 범위: 1974–2024
- 이름 기준 역 마커: 555
- 환승역 마커: 96
- 외부 이미지: 없음
- 실행 시 외부 요청: 없음
