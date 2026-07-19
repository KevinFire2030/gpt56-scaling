# Verification

검증 실행일: 2026-07-18
검증 위치: 현재 폴더

| 달성 기준 | 결과 | 실행 근거 |
|---|---|---|
| 1. report.md가 존재하고 맨 앞에 지정 요약 표가 포함됨 | PASS | `Path('report.md').is_file()` 및 비어 있지 않음 확인; 파일 첫 줄이 `| 구분 | 발견 내용 | 근거 (지점/기간/수치) | 권고 조치 |`와 일치 |
| 2. 데이터 품질 점검 번호 목록과 실행 제안 3가지 섹션이 모두 존재 | PASS | `## 1. 데이터 품질 점검`, `## 3. 실행 제안 3가지` 검색 통과; 번호 매긴 제안 3개 이상 확인 |
| 3. analysis.py가 현재 폴더에서 `python analysis.py`로 에러 없이 실행됨 | PASS | 실제 실행 결과 exit code 0; `wrote ... report.md`, `raw_rows=13091`, `corrected_rows=13152` 출력; `python -m py_compile analysis.py`도 통과 |

## 실행 로그 요약

- acceptance assertions passed
- analysis.py 실행 성공
- raw_rows=13,091
- duplicate_keys=31
- missing_keys=92
- high_outliers=2
- corrected_rows=13,152
- promo_uplift=17.5856%
- ticket_opportunity=₩335,451,108
