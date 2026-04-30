#!/usr/bin/env python3
"""
Generates assets/demo.gif — a synthesized animated terminal recording of a
/cto run. Uses PIL to render frames programmatically (no real screen
capture — that requires the user's terminal). Quality is lower than a real
recording but better than a placeholder.

Run:
  python3 assets/make_demo_gif.py
"""
from __future__ import annotations
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont

OUT = Path(__file__).parent / "demo.gif"
FONT_REG = "/System/Library/Fonts/SFNSMono.ttf"

# Dimensions — tuned for GitHub README readability + small file size
W, H = 880, 520
PAD_X, PAD_Y = 24, 22
LINE_H = 18
FONT_SIZE = 13

# Palette — terminal-dark
BG       = (24, 24, 27)
FG       = (240, 240, 240)
DIM      = (140, 140, 145)
GREEN    = (74, 222, 128)
YELLOW   = (251, 191, 36)
PURPLE   = (167, 139, 250)
ORANGE   = (249, 115, 22)
BLUE     = (96, 165, 250)
RED      = (248, 113, 113)
PROMPT   = (192, 132, 252)

# Each entry: (delay_in_frames, color, text)
# Delays are cumulative reveals — line N appears after `delay` frames from
# the start. This drives pacing.
SCRIPT: list[tuple[int, tuple[int, int, int], str]] = [
    (0,   PROMPT, "$ /cto \"AI business analyst for Indian D2C sellers\""),
    (4,   DIM,    ""),
    (6,   PURPLE, "▸ intake"),
    (8,   DIM,    "  slug: indian-d2c-analyst   state.json + messages.jsonl initialized"),
    (12,  PURPLE, "▸ context  (parallel: brain + refs)"),
    (15,  GREEN,  "  ✓ 8 chunks from Obsidian vault     ✓ 3 curated GH refs"),
    (18,  PURPLE, "▸ github-scout"),
    (20,  GREEN,  "  ✓ 7 prior-art repos · convergent stack: Next.js + FastAPI + Supabase"),
    (23,  PURPLE, "▸ /grill → /benchmark → /prd"),
    (26,  GREEN,  "  ✓ 6 forcing questions    ✓ 4-competitor matrix    ✓ 9 screens · 47 features"),
    (29,  PURPLE, "▸ prd-reviewer agent"),
    (31,  GREEN,  "  ✓ verdict: PASS"),
    (34,  DIM,    ""),
    (35,  ORANGE, "✋  PRD ready for review   ·   outputs/<slug>/prd/index.html"),
    (37,  YELLOW, "    [approved by human in 12m]"),
    (40,  DIM,    ""),
    (41,  PURPLE, "▸ /architect → /createplan → /advisor"),
    (43,  PURPLE, "▸ provisioning  (parallel)"),
    (45,  GREEN,  "  ✓ github  ✓ supabase  ✓ vercel  ✓ railway"),
    (48,  PURPLE, "▸ build  (parallel: frontend, backend, data, content engineers)"),
    (51,  GREEN,  "  ✓ 4 PRs · pre-merge PASS · autoresearch MERGE_SAFE"),
    (54,  PURPLE, "▸ mvp-reviewer agent"),
    (56,  GREEN,  "  ✓ 9/9 screens · 6/6 golden paths · verdict: PASS"),
    (58,  ORANGE, "✋  MVP ready for review   ·   localhost:3000"),
    (60,  YELLOW, "    [approved by human in 14m]"),
    (63,  DIM,    ""),
    (64,  PURPLE, "▸ /deploy → smoke test → /monitor"),
    (66,  GREEN,  "  ✓ vercel READY · railway 200 · sentry · plausible · uptime"),
    (69,  DIM,    ""),
    (70,  GREEN,  "✓ Production live: https://indian-d2c-analyst.vercel.app"),
    (72,  DIM,    "  cost: $5.42 / $10  ·  total: 2h 47m  ·  human attention: 26m"),
]

TOTAL_FRAMES = 90    # ~9 seconds at 10fps
FPS = 10
FRAME_MS = int(1000 / FPS)


def make_frame(font: ImageFont.FreeTypeFont, font_bold: ImageFont.FreeTypeFont,
               frame_idx: int) -> Image.Image:
    img = Image.new("RGB", (W, H), BG)
    draw = ImageDraw.Draw(img)

    # Title bar — Tanker · /cto autopilot
    title_bg = (32, 32, 38)
    draw.rectangle([(0, 0), (W, 32)], fill=title_bg)
    draw.text((PAD_X, 8), "● ● ●", font=font, fill=(120, 120, 120))
    draw.text((W // 2 - 80, 8), "Tanker  /cto  autopilot", font=font_bold, fill=DIM)

    # Render visible script lines
    y = 44
    for delay, color, text in SCRIPT:
        if frame_idx < delay:
            break
        draw.text((PAD_X, y), text, font=font, fill=color)
        y += LINE_H

    # Cursor: blinks on lines that are still revealing
    last_revealed = max((d for d, _, _ in SCRIPT if d <= frame_idx), default=0)
    if frame_idx == last_revealed and (frame_idx // 3) % 2 == 0:
        # find x position end of last line
        last_line = next((t for d, _, t in SCRIPT if d == last_revealed), "")
        bbox = draw.textbbox((PAD_X, y - LINE_H), last_line, font=font)
        cx = bbox[2] + 4
        cy = y - LINE_H + 2
        draw.rectangle([(cx, cy), (cx + 7, cy + 14)], fill=FG)

    # Footer hint
    footer = "tanishg98/tanker  ·  MIT  ·  github.com/tanishg98/tanker"
    draw.text((PAD_X, H - 24), footer, font=font, fill=DIM)

    return img


def main() -> None:
    OUT.parent.mkdir(parents=True, exist_ok=True)
    font = ImageFont.truetype(FONT_REG, FONT_SIZE)
    font_bold = ImageFont.truetype(FONT_REG, FONT_SIZE)

    frames = [make_frame(font, font_bold, i) for i in range(TOTAL_FRAMES)]

    # Convert to palettized images for smaller GIF
    pal_frames = []
    for f in frames:
        # Quantize using adaptive palette to keep colors crisp + small file
        p = f.convert("P", palette=Image.ADAPTIVE, colors=128)
        pal_frames.append(p)

    pal_frames[0].save(
        OUT,
        save_all=True,
        append_images=pal_frames[1:],
        duration=FRAME_MS,
        loop=0,
        optimize=True,
        disposal=2,
    )
    size_kb = OUT.stat().st_size / 1024
    print(f"wrote {OUT}  ({size_kb:.1f} KB, {TOTAL_FRAMES} frames @ {FPS}fps)")


if __name__ == "__main__":
    main()
