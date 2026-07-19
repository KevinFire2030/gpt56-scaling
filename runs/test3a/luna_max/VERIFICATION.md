# DANTE LABS — Gravity Trials

## Deliverables

- `index.html` — standalone Three.js r128 browser demo using the requested CDN URLs.
- `VERIFICATION.md` — implementation and verification notes.

## Implemented requirements

1. **Earth / Moon gravity comparison**
   - Environment toggle: `[ EARTH ]` / `[ MOON ]`.
   - Earth gravity: `9.81 m/s²`.
   - Moon gravity: `1.62 m/s²`.
   - The same launch speed (`V₀ = 4.20 m/s`) is used in both environments.
   - Apex and total flight time are calculated from `h = v₀² / (2g)` and `t = 2v₀/g`.

2. **DANTE LABS identity**
   - Fixed top bar with DL mark, `DANTE LABS`, and live simulation status.

3. **3D astronaut and fallback**
   - Loads `https://modelviewer.dev/shared-assets/models/Astronaut.glb` through `THREE.GLTFLoader`.
   - A procedural astronaut fallback is rendered immediately, so the scene remains usable if the GLB request is blocked or unavailable.

4. **Jump simulation**
   - `LAUNCH JUMP` button and Spacebar trigger a jump.
   - Real-time vertical position follows `y = v₀t − ½gt²`.
   - Telemetry changes through ascending, descending, landed states.

5. **Earth/Moon visual distinction**
   - Planet material, wireframe orbital grid, accent color, and telemetry change with the selected environment.
   - The trajectory line and active-body marker use the environment accent.

6. **Orbit and zoom controls**
   - Drag the canvas to orbit around the scene.
   - Mouse wheel zooms the camera in and out.

7. **Responsive HUD / controls**
   - Dark lab-style UI with responsive panel, environment segmented control, launch/reset controls, legend, and telemetry.

8. **Telemetry readout**
   - `[EARTH]/[MOON] gravity = …`
   - `[EARTH]/[MOON] apex height = …`
   - `[EARTH]/[MOON] flight time = …`
   - `[EARTH]/[MOON] landed` appears through the Mission State field after the jump completes.

## Expected physics values

Using `v₀ = 4.20 m/s`:

| Environment | g | Jump apex | Total flight time |
|---|---:|---:|---:|
| Earth | 9.81 m/s² | 0.90 m | 0.86 s |
| Moon | 1.62 m/s² | 5.44 m | 5.19 s |

The values are computed in the running page, not hard-coded into the telemetry output.

## Run / verify

Because the page uses CDN resources and a GLB fetch, serve the folder over HTTP rather than opening it with `file://`:

```bash
python -m http.server 8000
```

Open `http://localhost:8000/index.html` in a modern browser.

Manual verification checklist:

- [ ] Page opens with a rendered 3D planet, grid, trajectory, and astronaut/fallback astronaut.
- [ ] Earth is selected by default and shows `9.81 m/s²`, `0.90 m`, `0.86 s`.
- [ ] Moon changes the values to `1.62 m/s²`, `5.44 m`, `5.19 s`.
- [ ] `LAUNCH JUMP` animates the astronaut; state changes to ascending/descending and then `LANDED / TRIAL COMPLETE`.
- [ ] `RESET SCENE` returns the astronaut to the surface and state to `READY / GROUNDED`.
- [ ] Spacebar launches a trial.
- [ ] Canvas drag orbits and wheel zooms.
- [ ] If Astronaut.glb is unavailable, the procedural fallback still renders.

## Browser QA performed

The source was checked for the requested CDN URLs and the page was exercised through a local HTTP server. The browser console should be inspected for external-resource errors because CDN availability and browser network policy are environment-dependent. A failed GLB request is intentionally non-fatal because the procedural fallback is part of the implementation.
