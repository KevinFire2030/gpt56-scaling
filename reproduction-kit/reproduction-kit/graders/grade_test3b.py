#!/usr/bin/env python3
"""③-B 서울 지하철 성장 모션그래픽 채점기 — 데이터 무관 구조/타임라인 채점.

사용법: env -u PLAYWRIGHT_BROWSERS_PATH python3 grade_test3b.py --run-dir <combo dir>

데이터가 조합마다 달라 좌표 픽셀 대조는 불가능. 대신 "성장 서사가 성립하는가"를
관측 가능한 지표로 판정한다:
  G1 렌더  : 단일 index.html · 콘솔 에러 0 · 런타임 외부(http/https) 요청 0
  G2 타임라인: window.__mg.t 가 15.0초에 완결(±0.4s) 후 정지(year·lines_shown 홀드)
  G3 연도  : __mg.year 가 1974→2026 방향 단조 진행(대형 연도 표시 존재)
  G4 성장  : 노선 픽셀 커버리지가 시간에 따라 단조 증가 + 최종 프레임 색상 ≥8종
  G5 마커  : (반자동) 최종 프레임에서 역 마커/라벨 존재는 수동 확정
evaluator 통과: G1 and G2 and G4
사실 정확도(노선 수·색상·개통연도)와 정성은 SOURCES.md·프레임 수동 대조.
"""
import argparse
import colorsys
import sys
import time
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import emit, fail

T_TARGET = 15.0
T_TOL = 0.4
MILESTONES = [2.0, 5.0, 8.0, 11.0, 14.0]   # 커버리지 성장 측정 지점(초)


def analyze(png_path):
    """배경 대비 유효 노선 픽셀 비율 + 구분되는 색상(hue) 수."""
    from PIL import Image
    im = Image.open(png_path).convert("RGB").resize((270, 480))
    px = list(im.getdata())
    lit = 0
    hues = set()
    for r, g, b in px:
        h, s, v = colorsys.rgb_to_hsv(r / 255, g / 255, b / 255)
        # 배경(어두운 네이비)·회색 가이드 제외: 충분히 밝고 채도 있는 픽셀만 '노선'
        if v > 0.35 and s > 0.35:
            lit += 1
            hues.add(int(h * 24))       # 24구간 hue 버킷
    return lit / len(px), len(hues)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    ap.add_argument("--max-seconds", type=float, default=20.0, help="관측 상한(실시간)")
    args = ap.parse_args()
    run = Path(args.run_dir)
    html = run / "index.html"
    if not html.exists():
        return fail("test3b", "index.html 없음")

    from playwright.sync_api import sync_playwright
    logs, errors, ext_requests = [], [], []
    samples = []            # (mg_t, year, lines_shown)
    frames = {}             # milestone -> png path
    tmp = run / "_grade_frames"
    tmp.mkdir(exist_ok=True)

    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome", headless=True)
        pg = b.new_page(viewport={"width": 1080, "height": 1920}, device_scale_factor=1)
        pg.on("console", lambda m: (errors if m.type == "error" else logs).append(m.text))
        pg.on("pageerror", lambda e: errors.append(str(e)))

        def on_req(req):
            u = req.url
            if u.startswith("http://") or u.startswith("https://"):
                ext_requests.append(u)
        pg.on("request", on_req)

        pg.goto(html.resolve().as_uri(), timeout=60000)

        t0 = time.monotonic()
        next_ms = list(MILESTONES)
        last = None
        hold_since = None
        while time.monotonic() - t0 < args.max_seconds:
            mg = pg.evaluate("window.__mg || null")
            if mg and "t" in mg:
                samples.append((mg.get("t"), mg.get("year"), mg.get("lines_shown")))
                if next_ms and isinstance(mg.get("t"), (int, float)) and mg["t"] >= next_ms[0]:
                    ms = next_ms.pop(0)
                    fp = tmp / f"f_{int(ms)}.png"
                    pg.screenshot(path=str(fp)); frames[ms] = fp
                cur = (mg.get("year"), mg.get("lines_shown"))
                if isinstance(mg.get("t"), (int, float)) and mg["t"] >= T_TARGET:
                    if cur == last:
                        hold_since = hold_since or mg["t"]
                    else:
                        hold_since = None
                    last = cur
            pg.wait_for_timeout(200)
        final_fp = tmp / "f_final.png"; pg.screenshot(path=str(final_fp)); frames["final"] = final_fp
        b.close()

    has_mg = len(samples) > 0
    ts = [s[0] for s in samples if isinstance(s[0], (int, float))]
    years = [s[1] for s in samples if isinstance(s[1], (int, float))]
    lines = [s[2] for s in samples if isinstance(s[2], (int, float))]

    t_complete = max(ts) if ts else 0
    g2 = has_mg and (t_complete >= T_TARGET - T_TOL) and (t_complete <= T_TARGET + 2.0)
    year_ok = bool(years) and years == sorted(years) and min(years) <= 1980 and max(years) >= 2020

    cov = {}
    for ms, fp in frames.items():
        try:
            ratio, hcount = analyze(fp)
            cov[str(ms)] = {"lit_ratio": round(ratio, 4), "hues": hcount}
        except Exception as e:
            cov[str(ms)] = {"error": str(e)}
    ms_series = [cov[str(m)]["lit_ratio"] for m in MILESTONES if str(m) in cov and "lit_ratio" in cov[str(m)]]
    growth_monotone = (
        len(ms_series) >= 3
        and all(ms_series[i] <= ms_series[i + 1] + 0.002 for i in range(len(ms_series) - 1))
        and ms_series[-1] > ms_series[0] + 0.005
    )
    final_hues = cov.get("final", {}).get("hues", 0)
    color_div = final_hues >= 8

    g1 = html.exists() and len(errors) == 0 and len(ext_requests) == 0
    g3 = year_ok
    g4 = growth_monotone and color_div

    score = (25 * g1 + 25 * g2 + 15 * g3 + 25 * g4
             + 10 * (has_mg and lines and max(lines) >= 8))
    return emit({
        "test": "test3b", "run_dir": str(run),
        "gates": {
            "G1_render": g1, "console_errors": errors[:5], "runtime_ext_requests": ext_requests[:5],
            "G2_timeline": {"t_complete": round(t_complete, 2), "target": T_TARGET, "ok": bool(g2),
                            "hold_since": hold_since},
            "G3_year": {"min": min(years) if years else None, "max": max(years) if years else None,
                        "monotone": bool(years) and years == sorted(years), "ok": bool(g3)},
            "G4_growth": {"coverage_series": ms_series, "final_hues": final_hues,
                          "monotone": growth_monotone, "color_div>=8": color_div, "ok": bool(g4)},
            "lines_shown_max": max(lines) if lines else None,
            "sample_count": len(samples),
        },
        "coverage": cov,
        "score_auto": round(max(0, score), 1),
        "evaluator_pass": bool(g1 and g2 and g4),
        "note": "데이터가 조합마다 다르므로 좌표·역명 정확도(노선 수·색상·개통연도)와 정성(다크모드 미감·연출)은 "
                "SOURCES.md·최종 프레임 수동 대조로 확정. window.__mg 미구현 시 계측 불가 → 수동 실행 필요.",
    })


if __name__ == "__main__":
    sys.exit(main())
