# SOURCES

수집·가공일: 2026-07-19

## 1. 개통 연도와 노선 범위

### Wikipedia — Seoul Metropolitan Subway
- URL: https://en.wikipedia.org/wiki/Seoul_Metropolitan_Subway
- API 원문: https://en.wikipedia.org/w/api.php?action=parse&page=Seoul_Metropolitan_Subway&prop=wikitext&format=json&formatversion=2
- 사용 항목: `Lines and branches` 표의 Opening Year, 노선명, 계통 범위, 색상명.
- 가공: 표의 “Opening Year”를 각 노선의 등장 연도로 사용했다. 연장 개통 연도는 별도 신규 노선으로 세지 않았다.

### 한국어 위키백과 — 수도권 전철
- URL: https://ko.wikipedia.org/wiki/수도권_전철
- API 원문: https://ko.wikipedia.org/w/api.php?action=parse&page=수도권_전철&prop=wikitext&format=json&formatversion=2
- 사용 항목: 1974-08-15 수도권 전철 1호선 개통, 2022년 신림선, 2024년 GTX-A 개통 및 최근 연장 이력 교차 확인.

적용한 24개 노선과 최초 개통 연도:

| 노선 | 연도 | 노선 색상(HEX) |
|---|---:|---|
| 1호선 | 1974 | `#005DAA` |
| 2호선 | 1980 | `#00A44A` |
| 3호선 | 1985 | `#F47D30` |
| 4호선 | 1985 | `#00A9DC` |
| 수인분당선 | 1994 | `#F99D1C` |
| 5호선 | 1995 | `#936FB1` |
| 7호선 | 1996 | `#677718` |
| 8호선 | 1996 | `#D31145` |
| 인천 1호선 | 1999 | `#6FA0CE` |
| 6호선 | 2000 | `#C77539` |
| 경의중앙선 | 2005 | `#76C4A3` |
| 공항철도 | 2007 | `#3681B7` |
| 9호선 | 2009 | `#C6B182` |
| 경춘선 | 2010 | `#178C72` |
| 신분당선 | 2011 | `#EA545D` |
| 의정부경전철 | 2012 | `#FDA600` |
| 용인에버라인 | 2013 | `#4EA346` |
| 인천 2호선 | 2016 | `#ED8000` |
| 경강선 | 2016 | `#0054A6` |
| 우이신설선 | 2017 | `#B0CE18` |
| 서해선 | 2018 | `#8FC31E` |
| 김포골드라인 | 2019 | `#AD8605` |
| 신림선 | 2022 | `#6789CA` |
| GTX-A | 2024 | `#9A6292` |

주의: 경의중앙선과 수인분당선은 Wikipedia 표가 제시하는 계통의 최초 개통 연도(각각 2005, 1994)를 사용했다. 통합 운행 명칭이 생긴 연도와는 다르다.

## 2. 노선 형상·역 위치·연결 구조·색상

### Sinseiki / opensource-seoul-subway-map
- 저장소: https://github.com/Sinseiki/opensource-seoul-subway-map
- 사용 파일: `mapimage.svg`, `LICENSE`
- 고정 커밋: `06e3184f6951895919f0156cc08b396e84ecf429`
- 라이선스: MIT
- 사용 항목: 수도권 노선도의 SVG 선분 좌표, 일반역 원형 마커 좌표, 환승역 원형 마커, 역명 텍스트 위치, CSS 노선 색상.
- 가공:
  1. SVG의 색상별 `<line>` 요소를 24개 노선에 매핑했다.
  2. 동일 색상 계열의 반지름 2 SVG 원을 일반역 마커로 추출했다.
  3. 원본의 공통 환승 마커(`cls-87`) 중 둘 이상의 선택 노선 선분에서 5.2 SVG 단위 이내인 점만 환승역으로 채택했다.
  4. 환승역은 연결된 노선 가운데 두 번째로 이른 개통 연도 이후에 표시되도록 했다.
  5. 서울역·종로3가·홍대입구·왕십리·강남·잠실·김포공항은 원본 역명 위치와 가장 가까운 노선 점에 라벨을 배치했다.
  6. 원본 SVG 좌표계를 1080×1920 캔버스 안에 균일 축척으로 변환했다. 지도는 지리 축척도가 아니라 원본의 편집 가능한 도식 노선도다.
- 최종 내장량: 노선 선분 389개, 일반역 마커 523개, 조건부 환승 마커 119개, 주요 역 라벨 7개.

### OpenStreetMap / Overpass API 교차 확인
- 데이터 저작권: © OpenStreetMap contributors, ODbL 1.0
- URL: https://www.openstreetmap.org/copyright
- 질의 엔드포인트: https://overpass.kumi.systems/api/interpreter
- 사용 질의 개요: 서울권 bbox `(37.3,126.6,37.8,127.3)` 안의 `relation[route=subway]` 태그 조회.
- 조회 스냅샷의 `timestamp_osm_base`: 2026-06-12T12:14:17Z.
- 가공/용도: OSM relation의 `name:ko`, `ref`, `colour`, `from`, `to`, `wikidata`를 이용해 1~9호선과 신분당선 등의 명칭·색상·종점을 교차 확인했다. 최종 형상 좌표 자체는 위 MIT SVG를 사용했다.

## 3. 폰트

### Google Fonts — Noto Sans KR
- CSS 배포 URL: https://fonts.googleapis.com/css2?family=Noto+Sans+KR:wght@700&display=swap
- 폰트 프로젝트: https://fonts.google.com/noto/specimen/Noto+Sans+KR
- 라이선스: SIL Open Font License 1.1
- 가공: Noto Sans KR 700 TTF에서 화면에 필요한 한글·영문·숫자 글리프만 서브셋한 WOFF2(8,224 bytes)를 만들고 `data:font/woff2;base64,...`로 `index.html`에 내장했다.

## 4. 범위와 가정

- 최종 노선 수: 24개.
- 타임라인 표시 범위: 1974~2026.
- 내장된 노선의 최초 개통 연도 범위: 1974~2024.
- 2026년 개통 예정 노선은 “예정”을 사실상 개통으로 오인하지 않도록 포함하지 않았다. 2024년 GTX-A까지 완성된 24개 계통을 2026년 표시 시점까지 유지한다.
- 애니메이션은 노선별 최초 개통 연도를 기준으로 전체 현재 형상을 한 번에 성장시키는 설명적 모션그래픽이다. 세부 연장 구간별 개통 시점을 재현하는 역사 GIS는 아니다.
- 브라우저 실행 시에는 네트워크를 전혀 사용하지 않는다. 위 출처는 조사·제작 단계에서만 사용했다.
