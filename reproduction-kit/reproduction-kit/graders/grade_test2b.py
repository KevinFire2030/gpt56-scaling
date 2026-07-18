#!/usr/bin/env python3
"""②-B 사이트 클로닝 채점기 — Playwright 스크린샷 SSIM + DOM 체크.

사용법: env -u PLAYWRIGHT_BROWSERS_PATH python3 grade_test2b.py --run-dir test2b/<combo>
게이트: G1 콘솔에러 0 · G2 구조(DOM 텍스트 체크리스트) · G3 SSIM ≥0.75 · G4 375px 무스크롤 · G5 SSIM ≥0.90
evaluator 통과: G2 and SSIM ≥ 0.75
"""
import argparse
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent))
from common import emit, fail, image_ssim

BASE = Path(__file__).resolve().parent.parent.parent
ORIG = BASE / "test2b" / "_original_apple"
# 원본(apple.com/kr, 2026-07-12 스냅샷)의 구조 재현 체크리스트 (텍스트 존재 기반)
DOM_CHECKS = ["MacBook Air", "iPhone", "스토어", "iPad", "Watch",
              "AirPods", "고객지원", "구입하기"]


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--run-dir", required=True)
    args = ap.parse_args()
    run = Path(args.run_dir)
    html = run / "index.html"
    if not html.exists():
        return fail("test2b", "index.html 없음")

    from playwright.sync_api import sync_playwright
    errors = []
    with sync_playwright() as p:
        b = p.chromium.launch(channel="chrome", headless=True)
        pg = b.new_page(viewport={"width": 1440, "height": 900})
        pg.on("console", lambda m: errors.append(m.text) if m.type == "error" else None)
        pg.goto(html.resolve().as_uri(), wait_until="networkidle", timeout=60000)
        pg.wait_for_timeout(2500)
        body = pg.inner_text("body")
        shot = run / "_grade_1440.png"
        pg.screenshot(path=str(shot))
        pm = b.new_page(viewport={"width": 375, "height": 812})
        pm.goto(html.resolve().as_uri(), wait_until="networkidle", timeout=60000)
        pm.wait_for_timeout(1500)
        scroll_w = pm.evaluate("document.scrollingElement.scrollWidth")
        b.close()

    dom_hits = [c for c in DOM_CHECKS if c in body]
    dom_ok = len(dom_hits) >= 6  # 8개 중 6개 이상
    sim = image_ssim(shot, ORIG / "screenshot_1440_fold.png")
    no_hscroll = scroll_w <= 375 + 2

    score = (10 * (len(errors) == 0) + 25 * (len(dom_hits) / len(DOM_CHECKS))
             + 50 * min(1.0, sim / 0.90) + 15 * no_hscroll)
    return emit({
        "test": "test2b", "run_dir": str(run),
        "gates": {"G1_console_errors": len(errors),
                  "G2_dom": f"{len(dom_hits)}/{len(DOM_CHECKS)} {sorted(set(DOM_CHECKS)-set(dom_hits))}",
                  "G3_ssim": round(sim, 4), "G4_no_hscroll_375": no_hscroll,
                  "G5_ssim_high": sim >= 0.90},
        "score_auto": round(max(0, score), 1),
        "evaluator_pass": bool(dom_ok and sim >= 0.75),
    })


if __name__ == "__main__":
    sys.exit(main())
