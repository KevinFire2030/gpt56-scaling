# DANTE LABS — Gravity Field Test: Verification

## 실행 방법

이 폴더에서 정적 HTTP 서버를 실행한 뒤 브라우저로 엽니다. (GLTF/텍스처 CDN 로딩을 위해 `file://`보다 HTTP를 권장합니다.)

```bash
python -m http.server 8080
```

`http://localhost:8080/index.html`을 엽니다.

## 구현 범위 및 요구사항 대조

| # | 구현 / 검증 기준 | 상태 |
|---|---|---|
| 1 | Three.js WebGL 장면, 별 배경, 조명, 행성/착륙장/그리드, 우주비행사 애니메이션을 포함한다. | 구현 |
| 2 | 화면 상단에 `DANTE LABS` 브랜딩을 표시한다. | 구현 |
| 3 | Earth/Moon 버튼으로 중력 환경을 즉시 전환하며, 전환 중인 점프는 방지한다. | 구현 |
| 4 | 같은 이륙 속도(4.50 m/s)로 점프하고, 중력 차이에 따른 최고점·체공 시간을 이벤트에 기록한다. | 구현 |
| 5 | 8.00 m 높이의 Drop Test도 제공하고, 지상 도달까지의 시간을 기록한다. | 구현 |
| 6 | 매 프레임 물리 적분(`v -= g·dt`, `h += v·dt`)을 적용하고, 착지 시 높이를 0으로 고정한다. | 구현 |
| 7 | 환경 선택, JUMP/DROP TEST, 키보드 조작(공백/1/2/R), 실시간 중력·고도·속도 UI를 제공한다. | 구현 |
| 8 | 이벤트 스트림은 `[EARTH]/[MOON] jump_apex_m=…`, `fall_time_s=…`, `landed` 형식을 사용한다. | 구현 |

## 외부 자산 / CDN

- Three.js r128: `https://cdnjs.cloudflare.com/ajax/libs/three.js/r128/three.min.js`
- GLTFLoader r128: `https://cdn.jsdelivr.net/gh/mrdoob/three.js@r128/examples/js/loaders/GLTFLoader.js`
- Planet texture base: `https://cdn.jsdelivr.net/gh/mrdoob/three.js@r128/examples/textures/`
- Astronaut GLB: `https://modelviewer.dev/shared-assets/models/Astronaut.glb`

GLB 요청이 실패해도 화면을 사용할 수 있도록 코드 기반의 저폴리 우주비행사 fallback을 포함했습니다.

## 물리 기준값

공통 점프 초기 속도 `v0 = 4.50 m/s`.

- 최고점: `h = v0² / (2g)`
- 최고점에서 지상까지 이상적 낙하 시간: `t = v0 / g`
- 8m Drop Test: `t = √(2×8/g)`

| 환경 | g (m/s²) | 이론 점프 최고점 (m) | 이론 총 체공시간 (s) | 8m Drop Test (s) |
|---|---:|---:|---:|---:|
| EARTH | 9.81 | 1.03 | 0.92 | 1.28 |
| MOON | 1.62 | 6.25 | 5.56 | 3.14 |

브라우저의 프레임 단위 수치 적분 특성상 이벤트의 실제 출력값은 프레임 시간(`dt`, 최대 0.035초)만큼 이론값과 미세하게 다를 수 있습니다. `jump_apex_m`는 상승 속도가 0 이하가 되는 첫 프레임의 위치, `fall_time_s`는 JUMP 또는 DROP 시작부터 `landed`까지의 경과 시간입니다.

## 검증 절차

1. 페이지가 로드되면 3D 장면, `DANTE LABS`, Earth 선택 상태, 실시간 텔레메트리가 보이는지 확인한다.
2. `JUMP` 또는 `Space`를 누르고 이벤트 순서가 `jump_started` → `jump_apex_m=…` → `fall_time_s=…` → `landed`인지 확인한다.
3. Moon으로 전환하고 같은 점프를 실행한다. Moon의 최고점과 체공 시간이 Earth보다 커야 한다.
4. `DROP TEST`를 두 환경에서 실행한다. Moon의 착지 시간이 Earth보다 길어야 한다.
5. `1`, `2`, `R` 키로 각각 Earth, Moon, 리셋이 동작하는지 확인한다.
6. DevTools Console에 JavaScript error가 없는지 확인하고, 화면 크기를 바꿔 UI와 캔버스가 갱신되는지 확인한다.

## 성능 설계

- 렌더러 pixel ratio는 `min(devicePixelRatio, 2)`로 상한을 둡니다.
- 별은 단일 `THREE.Points` 드로우콜로 렌더링합니다.
- 애니메이션은 `requestAnimationFrame`과 delta-time 기반의 가벼운 적분만 수행합니다.
- 60 FPS는 기기·브라우저·네트워크/GLTF 로드 조건에 따라 달라지므로 보장 수치가 아니라 목표입니다. Scene은 해당 목표를 위해 저복잡도 geometry와 제한된 픽셀 비율을 사용합니다.
