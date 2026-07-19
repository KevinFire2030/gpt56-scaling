# SOURCES — 서울 수도권 지하철 성장 모션그래픽

작성일: 2026-07-19

## 데이터 범위

- 화면의 `21`개 서비스는 서울 지하철 1–9호선과 수도권의 주요 도시철도·광역전철(경의·중앙, 수인·분당, 인천 1·2, 공항철도, 경춘, 신분당, 우이신설, 서해, 김포골드, GTX-A)을 포함한다.
- 연도 범위는 1974–2026이다. 2026년 시점에 개통된 노선만 사용했으며, 계획·공사 중 노선은 넣지 않았다.
- `개통 연도`는 그 서비스가 처음 영업 개시한 해이다. 전체 연장/직결/통합의 모든 연혁을 표현하지 않는다. 예외적으로 화면에는 ‘수인·분당선 통합’(2020)을 별도 성장 이벤트로 넣어 수인선 완전 개통 및 통합 운행을 표현했다.
- SVG/지리 타일을 복사하지 않고, 아래의 공개 지도·노선 자료에서 확인한 실제 역명과 연결 순서를 바탕으로 한 **내장형 개략(topological) 도식**을 만들었다. 좌표는 화면 판독성을 위한 작가 가공 좌표이며 축척 지도나 전체 역 목록이 아니다.

## 공개 출처

1. 서울교통공사, `Subway Line Information` 및 노선도
   - https://www.seoulmetro.co.kr/en/cyberStation.do
   - 노선 색상·노선명 대조에 사용.
2. Wikipedia, `Seoul Metropolitan Subway`
   - https://en.wikipedia.org/wiki/Seoul_Metropolitan_Subway
   - 운영 체계, 노선의 범위 및 역사 교차검증에 사용.
3. Wikipedia의 각 노선 문서 (예: `Seoul Subway Line 1`)
   - https://en.wikipedia.org/wiki/Seoul_Subway_Line_1
   - 각 서비스의 최초 개통연도와 주요 역 순서를 교차검증. 같은 형식의 Line 2–9, Airport Railroad, Shinbundang Line, Ui-Sinseol Line, Seohae Line, Gimpo Goldline, Gyeongchun Line, Gyeongui–Jungang Line, Suin–Bundang Line, Incheon Subway Line 1/2, GTX-A 문서를 참조.
4. OpenStreetMap Wiki, `Seoul Subway`
   - https://wiki.openstreetmap.org/wiki/Seoul_Subway
   - 공개 OSM 관계(relation)·노선 태그를 확인하는 출발점으로 사용.
5. OpenStreetMap 데이터
   - https://www.openstreetmap.org/
   - 역명과 선형 연결을 시각적으로 대조. ODbL 1.0.
6. 국가철도공단, GTX-A 개통 관련 공개 안내
   - https://www.kr.or.kr/
   - GTX-A의 2024년 최초 개통 사실 교차검증에 사용.

## 가공 방법

1. 출처에서 각 서비스의 실제 최초 영업 개시 연도와 대표 역을 확인했다.
2. 한 화면에서 시간적 성장을 읽을 수 있도록 실제 역 위치의 상대적 방향과 환승 관계를 보존한 소수의 앵커 역 폴리라인으로 단순화했다.
3. 색상은 공식/통상 노선색을 적용했다. 각 선의 이름·최초 개통연도·색상·앵커 좌표·역명은 `index.html`의 `L` 배열 안에 모두 내장했다.
4. 환승 마커는 가공된 도식에서 동일/근접 앵커를 공유하는 지점에 밝은 큰 원으로 표시한다. 따라서 모든 실제 환승역의 완전 목록을 주장하지 않는다.
5. 외부 데이터, 타일, 폰트, 이미지, CSS, JavaScript를 런타임에 요청하지 않는다.

## 검증 대상 최종 데이터

- 서비스/성장 이벤트: 21
- 최초 이벤트: 1호선, 1974
- 마지막 이벤트: GTX-A, 2024
- 재생 종료 연도 표시: 2026
- 주요 앵커 역명은 실제 역명만 사용.
