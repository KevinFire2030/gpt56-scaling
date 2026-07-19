# DANTE LABS — Earth vs Moon Jump Lab

## 실행

이 결과물은 빌드 과정이 없는 단일 `index.html`입니다. 브라우저의 `file://` 보안 정책 대신 로컬 HTTP 서버로 여는 것을 권장합니다.

```bash
cd E:/ax/PRJs/gpt56-scaling/runs/test3a/sol_max
python -m http.server 8899
```

브라우저에서 `http://127.0.0.1:8899/index.html`을 엽니다. Three.js, GLTFLoader, 텍스처, Astronaut GLB는 요청된 CDN에서 로드되므로 첫 실행 시 인터넷 연결이 필요합니다.

조작:

- `RUN JUMP TEST` 또는 `Space`: 두 환경에서 동일한 초기속도로 점프
- `PAUSE / RESUME`: 물리 시뮬레이션 일시정지/재개
- `RESET` 또는 `R`: 초기 상태 복원
- 마우스 드래그: 두 장면의 카메라를 동일하게 회전
- 휠: 두 장면의 카메라를 동일하게 확대/축소

## 요구사항 1~8 확인

1. **동일한 우주비행사, 다른 환경 비교 — PASS**
   - 같은 Astronaut GLB를 복제하여 양쪽에 동일한 스케일, 자세, 재질로 배치했습니다.
   - 화면을 정확히 50:50으로 나누고, 지구는 푸른 대기·초록 지면, 달은 무대기 별빛·회색 월면으로 구분했습니다.
   - 양쪽 카메라는 같은 yaw, pitch, distance 값을 공유하므로 드래그/줌 시 동일하게 움직입니다.

2. **DANTE LABS 브랜딩 — PASS**
   - 상단 고정 헤더에 `DANTE LABS`와 실험 식별자 `Comparative Gravity Research Unit / Experiment 04`를 표시했습니다.

3. **같은 점프 조건에서 중력 차이를 시각화 — PASS**
   - 양쪽 모두 동일한 초기 수직속도 `3.2 m/s`를 사용합니다.
   - 지구 중력 `9.81 m/s²`, 달 중력 `1.62 m/s²`를 독립 적용합니다.
   - 결과적으로 달에서 더 높고 오래 체공하며, 우주비행사와 그림자가 연속적으로 움직입니다.

4. **물리 기반 상승·정점·하강·착지 — PASS**
   - 고정 물리 스텝 `1/120 s`와 등가속도 운동식 `y(t+dt)=y+v·dt−½g·dt²`를 사용합니다.
   - 상태는 `READY → ASCENDING → DESCENDING → LANDED` 순서로 전환됩니다.
   - 정점과 착지 시점은 스텝 내부를 해석적으로 보간해 프레임레이트에 의존하지 않습니다.

5. **두 환경 동시 비교 — PASS**
   - 한 번의 버튼/Space 입력으로 두 점프가 같은 시각에 시작됩니다.
   - 각 환경의 고도, 속도, 정점, 낙하시간, 상태를 독립적으로 실시간 표시합니다.

6. **장면 디테일 및 시각 피드백 — PASS**
   - 조명, soft shadow, fog, 별, 월면 crater, grid, 표면 텍스처를 적용했습니다.
   - 고도에 따라 그림자의 크기와 불투명도가 감소하고, 체공 중 미세 자세 변화가 적용됩니다.
   - GLB 로드 실패 시에도 기능이 멈추지 않도록 procedural EVA suit fallback을 제공합니다.

7. **UI 및 조작 — PASS**
   - 점프, 일시정지/재개, 리셋, 키보드 단축키, 동기화 orbit/zoom을 구현했습니다.
   - 반투명 계기판, 포커스 표시, `aria-live`, 모바일 breakpoint를 포함했습니다.

8. **이벤트 로그/계측값 — PASS**
   - 실행 전 `READY`, 상승 중 `ASCENDING`, 하강 중 `DESCENDING`, 착지 후 `LANDED`를 양쪽에 표시합니다.
   - 착지 후 표시 예:
     - `[EARTH] jump_apex_m=0.52`
     - `[MOON] jump_apex_m=3.16`
     - `[EARTH] fall_time_s=0.33`
     - `[MOON] fall_time_s=1.98`
     - `[EARTH] landed`
     - `[MOON] landed`

## 물리 계산 검증

입력:

- 초기 수직속도 `v₀ = 3.2 m/s`
- 지구 `g = 9.81 m/s²`
- 달 `g = 1.62 m/s²`
- 시작/착지 고도 `y = 0 m`
- 공기저항 없음

공식:

- 정점 고도: `h = v₀² / (2g)`
- 정점부터 지면까지 낙하시간: `t_fall = v₀ / g`
- 총 체공시간: `t_total = 2v₀ / g`

| 환경 | 이론 정점(m) | 실행 측정 정점(m) | 이론 낙하시간(s) | 실행 측정 낙하시간(s) | 총 체공시간(s) |
|---|---:|---:|---:|---:|---:|
| EARTH | 0.521916 | 0.5219164118 | 0.326198 | 0.3261977574 | 0.6523955148 |
| MOON | 3.160494 | 3.1604938272 | 1.975309 | 1.9753086420 | 3.9506172840 |

UI는 가독성을 위해 각각 `0.52 m / 0.33 s`, `3.16 m / 1.98 s`로 반올림합니다.

## 실제 브라우저 검증 기록

검증 URL: `http://127.0.0.1:8899/index.html?verify=3`

- 페이지 제목: `DANTE LABS — Earth vs Moon Jump Lab`
- Three.js revision: `128`
- GLB 상태: `ASTRONAUT GLB · READY`
- WebGL canvas: 1개, scissor rendering으로 좌우 2개 viewport 출력
- 점프 완료 상태: EARTH `LANDED`, MOON `LANDED`
- 브라우저 console message: 0개
- JavaScript error: 0개
- 추출한 inline JavaScript `node --check`: exit code 0
- 2초 requestAnimationFrame 측정: 121 frames / 2.009 s
  - 평균 frame time: `16.6825 ms`
  - 추정 FPS: `59.943`
  - 최대 frame time: `16.9 ms`
- 시각 확인: 두 모델 정상 가시, 좌우 환경 명확, 완료 계측값 정상, 제목/상태/UI 겹침 없음

## 외부 리소스

- Three.js r128: `https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js`
- GLTFLoader r128: `https://cdn.jsdelivr.net/gh/mrdoob/three.js@r128/examples/js/loaders/GLTFLoader.js`
- Texture root: `https://cdn.jsdelivr.net/gh/mrdoob/three.js@r128/examples/textures/`
- Astronaut GLB: `https://modelviewer.dev/shared-assets/models/Astronaut.glb`

## 파일 구성

```text
index.html       # CSS, UI, Three.js 장면, 물리, 입력을 모두 포함한 단일 실행 파일
VERIFICATION.md  # 실행법, 요구사항 매핑, 계산 및 실제 검증 증거
```
