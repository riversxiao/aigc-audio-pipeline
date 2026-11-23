#!/usr/bin/env python3
"""Reusable museum-grade 1:1 Ximalaya burnished-gold serif album cover compositor."""

from __future__ import annotations

import argparse
from pathlib import Path
import shutil
from PIL import Image, ImageDraw, ImageFilter, ImageFont

SERIF_PATH = "/usr/share/fonts/opentype/noto/NotoSerifCJK-Bold.ttc"
SANS_PATH = "/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"


def compose_ximalaya_cover(
    *,
    src_image: Path,
    out_dir: Path,
    slug: str,
    kicker: str,
    title: str,
    subtitle: str,
    tagline: str,
    title_scale: float | None = None,
    title_track_scale: float | None = None,
) -> tuple[Path, Path]:
    out_dir.mkdir(parents=True, exist_ok=True)
    clean_dst = out_dir / f"{slug}_cover_clean_1x1.jpg"
    titled_dst = out_dir / f"{slug}_ximalaya_cover_titled_1x1.jpg"
    shutil.copyfile(src_image, clean_dst)

    img = Image.open(clean_dst).convert("RGBA")
    w, h = img.size

    # Smooth top + bottom vignettes for editorial legibility without obscuring art center
    overlay = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    od = ImageDraw.Draw(overlay)
    top_h = int(h * 0.36)
    for y in range(top_h):
        t = 1.0 - (y / top_h)
        alpha = int(208 * (t ** 1.30))
        od.line([(0, y), (w, y)], fill=(10, 8, 6, alpha))
    bot_start = int(h * 0.84)
    bot_h = h - bot_start
    for y in range(bot_start, h):
        t = (y - bot_start) / bot_h
        alpha = int(218 * (t ** 1.20))
        od.line([(0, y), (w, y)], fill=(9, 7, 5, alpha))
    img = Image.alpha_composite(img, overlay)

    # Hairline antique-gold frame
    frame = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    fd = ImageDraw.Draw(frame)
    pad = int(w * 0.025)
    fd.rectangle([pad, pad, w - pad, h - pad], outline=(228, 190, 118, 155), width=2)
    img = Image.alpha_composite(img, frame)

    # Auto-scale main title smoothly by character count
    n_chars = len(title)
    if title_scale is None:
        if n_chars <= 3:
            title_scale = 0.126
        elif n_chars == 4:
            title_scale = 0.114
        elif n_chars == 5:
            title_scale = 0.102
        elif n_chars == 6:
            title_scale = 0.092
        else:
            title_scale = 0.080
    if title_track_scale is None:
        if n_chars <= 3:
            title_track_scale = 0.048
        elif n_chars == 4:
            title_track_scale = 0.036
        elif n_chars == 5:
            title_track_scale = 0.022
        elif n_chars == 6:
            title_track_scale = 0.015
        else:
            title_track_scale = 0.010

    f_kicker = ImageFont.truetype(SANS_PATH, int(w * 0.025), index=2)
    f_title = ImageFont.truetype(SERIF_PATH, int(w * title_scale), index=2)
    f_sub = ImageFont.truetype(SERIF_PATH, int(w * 0.035), index=2)
    f_tag = ImageFont.truetype(SANS_PATH, int(w * 0.024), index=2)

    def draw_tracked(draw, text: str, y: int, font, fill, tracking: int = 0, shadow: bool = True) -> float:
        widths = [draw.textlength(ch, font=font) for ch in text]
        total_w = sum(widths) + tracking * max(0, len(text) - 1)
        x = (w - total_w) / 2.0
        for ch, cw in zip(text, widths):
            if shadow:
                draw.text((x + 2, y + 3), ch, font=font, fill=(6, 4, 2, 220))
            draw.text((x, y), ch, font=font, fill=fill)
            x += cw + tracking
        return total_w

    txt_layer = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    td = ImageDraw.Draw(txt_layer)
    draw_tracked(td, kicker, int(h * 0.044), f_kicker, (238, 214, 166, 240), tracking=int(w * 0.004))

    title_track = int(w * title_track_scale)
    title_y = int(h * 0.078)
    mask = Image.new("L", (w, h), 0)
    md = ImageDraw.Draw(mask)
    widths = [md.textlength(ch, font=f_title) for ch in title]
    total_tw = sum(widths) + title_track * max(0, len(title) - 1)
    tx = (w - total_tw) / 2.0
    shad = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    sd = ImageDraw.Draw(shad)
    cur_x = tx
    for ch, cw in zip(title, widths):
        sd.text((cur_x + 4, title_y + 6), ch, font=f_title, fill=(5, 4, 2, 238))
        md.text((cur_x, title_y), ch, font=f_title, fill=255)
        cur_x += cw + title_track
    shad = shad.filter(ImageFilter.GaussianBlur(radius=4))
    img = Image.alpha_composite(img, shad)

    grad = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gd = ImageDraw.Draw(grad)
    bbox = mask.getbbox()
    y0, y1 = bbox[1], bbox[3]
    for y in range(y0, y1 + 1):
        t = (y - y0) / max(1, (y1 - y0))
        if t < 0.45:
            u = t / 0.45
            r, g, b = int(255 - 12 * u), int(242 - 34 * u), int(198 - 66 * u)
        else:
            u = (t - 0.45) / 0.55
            r, g, b = int(243 - 54 * u), int(208 - 68 * u), int(132 - 64 * u)
        gd.line([(0, y), (w, y)], fill=(r, g, b, 255))
    gold_title = Image.new("RGBA", (w, h), (0, 0, 0, 0))
    gold_title.paste(grad, (0, 0), mask)
    img = Image.alpha_composite(img, gold_title)

    # Dynamic breathing room below title bottom edge
    sub_y = max(int(h * 0.238), y1 + int(h * 0.028))
    sub_w = draw_tracked(td, subtitle, sub_y, f_sub, (246, 224, 178, 248), tracking=int(w * 0.005))
    rule_y = sub_y + int(w * 0.022)
    gap = int(w * 0.024)
    rule_len = int(w * 0.088)
    left_x1 = int((w - sub_w) / 2 - gap)
    left_x0 = max(pad + 18, left_x1 - rule_len)
    right_x0 = int((w + sub_w) / 2 + gap)
    right_x1 = min(w - pad - 18, right_x0 + rule_len)
    if left_x1 > left_x0 + 10:
        td.line([(left_x0, rule_y), (left_x1, rule_y)], fill=(228, 190, 118, 190), width=2)
    if right_x1 > right_x0 + 10:
        td.line([(right_x0, rule_y), (right_x1, rule_y)], fill=(228, 190, 118, 190), width=2)

    draw_tracked(td, tagline, int(h * 0.912), f_tag, (242, 224, 192, 240), tracking=int(w * 0.003))

    img = Image.alpha_composite(img, txt_layer).convert("RGB")
    img.save(titled_dst, quality=95, subsampling=0)
    return clean_dst, titled_dst


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--src", required=True)
    p.add_argument("--out-dir", required=True)
    p.add_argument("--slug", required=True)
    p.add_argument("--kicker", required=True)
    p.add_argument("--title", required=True)
    p.add_argument("--subtitle", required=True)
    p.add_argument("--tagline", required=True)
    args = p.parse_args()
    c, t = compose_ximalaya_cover(
        src_image=Path(args.src),
        out_dir=Path(args.out_dir),
        slug=args.slug,
        kicker=args.kicker,
        title=args.title,
        subtitle=args.subtitle,
        tagline=args.tagline,
    )
    print(f"✅ {c} | {t}")
