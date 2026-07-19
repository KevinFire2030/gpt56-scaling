# 자체 검증 결과

- 대상 파일: `입력데이터/영수증/R01.png` ~ `R20.png` (20장)
- 출력 파일: `runs/test1a/terra_m/receipts.json`
- JSON 파싱: 성공
- 영수증 객체 수: 20개
- receipt_id: `R001`부터 `R020`까지 순서대로 정확히 20개 확인
- 필수 영수증 키: 모든 객체에 `receipt_id`, `store_name`, `date`, `items`, `subtotal`, `tax`, `total`, `flags` 존재 확인
- 필수 품목 키: 모든 품목에 `name`, `qty`, `unit_price`, `amount` 존재 확인
- 금액 형식: subtotal, tax, total, unit_price, amount는 모두 KRW 정수 또는 해당 없음 규칙을 충족
- 합계 검증: 모든 영수증에서 `subtotal + tax = total` 확인
- 품목 산술 검증: 수량이 판독된 모든 품목에서 `qty × unit_price = amount` 확인
- 예외: R019 감자튀김의 수량은 얼룩으로 가려져 `null`로 기록했으며, 사유를 flags에 기록
- 환산: R007은 원본 영수증의 `금액단위: 천원` 표기를 KRW 정수로 환산했으며, 사유를 flags에 기록
