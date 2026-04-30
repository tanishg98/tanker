#!/usr/bin/env python3
"""
Captures screenshots of https://persona-studio-lime.vercel.app and stitches
them into a hero GIF for the Tanker README. Replaces the synthesized
terminal animation with shots of the real product /cto built.
"""
from __future__ import annotations
import time
from pathlib import Path
from PIL import Image
from playwright.sync_api import sync_playwright

OUT_DIR = Path(__file__).parent
SHOTS_DIR = OUT_DIR / "persona-shots"
SHOTS_DIR.mkdir(exist_ok=True)

URL = "https://persona-studio-lime.vercel.app"
W, H = 1280, 800   # 16:10 — clean readme hero ratio


def capture() -> list[Path]:
    files: list[Path] = []
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        ctx = browser.new_context(viewport={"width": W, "height": H},
                                  device_scale_factor=2)  # retina-quality
        page = ctx.new_page()

        # 1. Landing hero
        page.goto(URL, wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(1500)  # let any animations settle
        f = SHOTS_DIR / "01-hero.png"
        page.screenshot(path=str(f), full_page=False)
        files.append(f)

        # 2. Scroll a bit and snap features
        page.evaluate("window.scrollTo({top: 700, behavior: 'instant'})")
        page.wait_for_timeout(800)
        f = SHOTS_DIR / "02-features.png"
        page.screenshot(path=str(f), full_page=False)
        files.append(f)

        # 3. Scroll more
        page.evaluate("window.scrollTo({top: 1500, behavior: 'instant'})")
        page.wait_for_timeout(800)
        f = SHOTS_DIR / "03-mid.png"
        page.screenshot(path=str(f), full_page=False)
        files.append(f)

        # 4. Try to enter the studio if there's a CTA. Otherwise stay on landing.
        try:
            page.evaluate("window.scrollTo({top: 0, behavior: 'instant'})")
            page.wait_for_timeout(500)
            cta = page.query_selector("a:has-text('Get started'), a:has-text('Start'), a:has-text('Try'), button:has-text('Get started'), button:has-text('Start')")
            if cta:
                cta.click()
                page.wait_for_timeout(2500)
                f = SHOTS_DIR / "04-studio.png"
                page.screenshot(path=str(f), full_page=False)
                files.append(f)
        except Exception as e:
            print(f"  (studio nav skipped: {e})")

        # 5. Full-page tall screenshot for static fallback
        page.goto(URL, wait_until="networkidle", timeout=30000)
        page.wait_for_timeout(1500)
        f = SHOTS_DIR / "00-fullpage.png"
        page.screenshot(path=str(f), full_page=True)
        files.append(f)

        browser.close()
    return files


def make_gif(shot_files: list[Path]) -> Path:
    # Use only the viewport-sized shots for the GIF (skip full-page tall one)
    frames_src = [f for f in shot_files if "fullpage" not in f.name]
    print(f"  building gif from {len(frames_src)} screens")

    frames: list[Image.Image] = []
    for f in frames_src:
        img = Image.open(f).convert("RGB")
        # Downscale 2x retina to 1x for GIF size
        img = img.resize((W, H), Image.LANCZOS)
        # Quantize for GIF
        p = img.convert("P", palette=Image.ADAPTIVE, colors=128)
        # Hold each screen for ~2 seconds
        for _ in range(20):
            frames.append(p)

    out = OUT_DIR / "demo.gif"
    frames[0].save(
        out,
        save_all=True,
        append_images=frames[1:],
        duration=100,   # 10fps × 20 dupes per frame = 2s/screen
        loop=0,
        optimize=True,
        disposal=2,
    )
    print(f"  wrote {out} ({out.stat().st_size / 1024:.1f} KB)")
    return out


def make_hero(shot_files: list[Path]) -> Path:
    # Standalone PNG hero from the landing screenshot
    src = next((f for f in shot_files if f.name == "01-hero.png"), None)
    if not src:
        return Path()
    img = Image.open(src).convert("RGB")
    img = img.resize((W, H), Image.LANCZOS)
    out = OUT_DIR / "hero.png"
    img.save(out, optimize=True)
    print(f"  wrote {out} ({out.stat().st_size / 1024:.1f} KB)")
    return out


def main() -> None:
    print("capturing screenshots…")
    shots = capture()
    print(f"  captured {len(shots)} screens")
    for s in shots:
        print(f"    {s.name}  ({s.stat().st_size / 1024:.1f} KB)")
    make_gif(shots)
    make_hero(shots)


if __name__ == "__main__":
    main()
