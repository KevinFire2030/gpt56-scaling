# SOURCES.md

## 작업 범위

- 산출물: `index.html` 단일 파일 모션그래픽
- 최종 노선 수: 26개(서울 1~9호선, 수도권 광역·경전철·인천·공항·GTX 노선 포함)
- 개통 연도 범위: 1974–2024년의 실제 개통 노선을 사용하고, 타임라인 표기는 요청대로 2026년까지 유지
- 2026은 2026년 현재 시점을 보여주는 종점 연도이며, 2026년에 새로 개통한 노선을 임의로 추가하지 않음
- 조사 시각(UTC): 2026-07-18T23:33:29Z

## 원자료

1. Wikipedia, **Seoul Metropolitan Subway**
   - https://en.wikipedia.org/wiki/Seoul_Metropolitan_Subway
   - 수도권 전철의 노선 체계, 노선별 개통·운영 정보, 직결/광역 노선 구분을 교차 확인하는 기본 자료.
   - MediaWiki API의 최신 페이지 추출본과 페이지 본문을 확인했습니다.
2. Wikipedia, **Seoul Subway Line 1** through **Seoul Subway Line 9**
   - https://en.wikipedia.org/wiki/Seoul_Subway_Line_1
   - https://en.wikipedia.org/wiki/Seoul_Subway_Line_2
   - https://en.wikipedia.org/wiki/Seoul_Subway_Line_3
   - https://en.wikipedia.org/wiki/Seoul_Subway_Line_4
   - https://en.wikipedia.org/wiki/Seoul_Subway_Line_5
   - https://en.wikipedia.org/wiki/Seoul_Subway_Line_6
   - https://en.wikipedia.org/wiki/Seoul_Subway_Line_7
   - https://en.wikipedia.org/wiki/Seoul_Subway_Line_8
   - https://en.wikipedia.org/wiki/Seoul_Subway_Line_9
   - 각 도시철도 노선의 개통 시점과 공식 노선 색상 표를 교차 확인했습니다.
3. OpenStreetMap Wiki, **Seoul**
   - https://wiki.openstreetmap.org/wiki/Seoul
   - 공개 지도 데이터의 사용 조건과 서울 지역 매핑 참고 링크 확인.
4. OpenStreetMap API
   - https://api.openstreetmap.org/api/0.6/
   - 공개 API 엔드포인트 접근 가능 여부를 확인했습니다. 브라우저 실행 시 외부 요청이 없도록 OSM 타일/오버레이는 임베드하지 않았습니다.
5. Wikimedia Commons, **Seoul subway linemap.svg**
   - https://commons.wikimedia.org/wiki/File:Seoul_subway_linemap.svg
   - 공개 노선도의 색상·환승역·노선 연결 관계를 시각적으로 교차 확인했습니다.
6. Wikipedia, **GTX-A**
   - https://en.wikipedia.org/wiki/GTX-A
   - 2024년 수서–동탄 구간 개통 사실을 교차 확인했습니다.

## 가공 방법

- 노선별 `year`, `color`, `pts`, `labels`를 `index.html` 안의 자바스크립트 상수로 인라인했습니다.
- `year`는 각 노선이 최초로 운행을 시작한 시점을 기준으로 정렬했습니다. 동일 연도인 1985, 1996, 2009, 2016 노선은 같은 연도 구간에서 함께 등장합니다.
- 1~9호선의 색상은 공개 노선도에서 통용되는 색상값을 사용했습니다. 광역·경전철 색상은 공개 노선도에서 해당 계통을 식별하는 색을 사용했습니다. 원자료가 단일 HEX 표를 제공하지 않는 경우에는 식별용 근사값을 고정했습니다.
- `pts`는 지리 좌표가 아니라 1080×1920 화면에 맞춘 개략 좌표입니다. 인천·공항·서울 도심·동남권·동북권·경기 외곽의 상대적 위치와 주요 환승 연결 구조를 보존하는 방식으로 단순화했습니다. 따라서 실제 지도 축척이나 정확한 선형을 주장하지 않습니다.
- 실제 역명은 공개 자료에서 확인되는 주요 역만 라벨로 표시했습니다: 서울역, 시청, 강남, 잠실, 청량리, 용산, 홍대입구, 종로3가, 고속터미널, 김포공항, 인천공항, 신도림, 사당.
- 모든 노선은 처음부터 낮은 불투명도의 가이드로 그린 뒤, 개통 연도에 대응하는 시점부터 색상 경로가 순차적으로 드러납니다.

## 노선 데이터(최초 개통 연도 기준)

| ID | 표시명 | 연도 | 색상 |
|---|---|---:|---|
| 1 | 1호선 | 1974 | #0052A4 |
| 2 | 2호선 | 1980 | #00A84F |
| 3 | 3호선 | 1985 | #EF7C1C |
| 4 | 4호선 | 1985 | #00A5DE |
| B | 분당선 | 1994 | #F5A200 |
| 5 | 5호선 | 1995 | #996CAC |
| 7 | 7호선 | 1996 | #747F00 |
| 8 | 8호선 | 1996 | #E6186C |
| IC1 | 인천 1호선 | 1999 | #7CA8D5 |
| 6 | 6호선 | 2000 | #CD7C2F |
| J | 중앙선 | 2005 | #77C4A3 |
| AREX | 공항철도 | 2007 | #3681B7 |
| 9 | 9호선 | 2009 | #BDB092 |
| GJ | 경의선(현 경의·중앙선) | 2009 | #77C4A3 |
| GC | 경춘선 | 2010 | #178C72 |
| SB | 신분당선 | 2011 | #D31145 |
| UIJ | 의정부경전철 | 2012 | #F7B32B |
| SUIN | 수인선 | 2012 | #F5A200 |
| EV | 용인경전철 | 2013 | #56A6D9 |
| G | 경강선 | 2016 | #0054A6 |
| IC2 | 인천 2호선 | 2016 | #F5A200 |
| UIS | 우이신설선 | 2017 | #B7C5D0 |
| SEOHAE | 서해선 | 2018 | #8FC31F |
| GIMPO | 김포골드라인 | 2019 | #AD8605 |
| SILLIM | 신림선 | 2022 | #6789CA |
| GTXA | GTX-A | 2024 | #3D7FC1 |

주의: 경의선은 2009년 서울역–문산 구간 운행 시작을 표시하며, 중앙선과의 직결로 현재 경의·중앙선 계통이 된 2014년 통합은 별도 물리 노선으로 중복 표시하지 않았습니다. 수인선은 2012년 1차 개통을 기준으로 표시하며, 2020년 수인–분당선 직결도 중복 노선으로 만들지 않았습니다. GTX-A는 공개 자료상 2024년 3월 수서–동탄 구간 개통을 기준으로 하며, 2026년은 시간축의 종점일 뿐 신규 노선을 추정하지 않았습니다.
