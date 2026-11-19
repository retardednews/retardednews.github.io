"""Builds 1080x1350 Facebook image cards: story photo, dark fade, headline, brand tag, photo credit.

Usage:  python tools/make_cards.py SRC_DIR OUT_DIR [slug ...]
SRC_DIR holds <slug>.jpg source photos (the story's Commons image). Cards are written to OUT_DIR/<slug>.jpg.
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORIES = {s["slug"]: s for s in json.load(open(os.path.join(ROOT, "tools", "stories.json"), encoding="utf-8"))}
F = "C:/Windows/Fonts/"
W, H = 1080, 1350
RED = (200, 16, 46)
PAD = 64


def font(name, size):
    return ImageFont.truetype(F + name, size)


def wrap(draw, text, fnt, width):
    lines, line = [], ""
    for word in text.split():
        test = (line + " " + word).strip()
        if draw.textlength(test, font=fnt) <= width:
            line = test
        else:
            lines.append(line)
            line = word
    lines.append(line)
    return lines


def cover(img):
    scale = max(W / img.width, H / img.height)
    img = img.resize((round(img.width * scale), round(img.height * scale)), Image.LANCZOS)
    left = (img.width - W) // 2
    top = max(0, (img.height - H) // 3)  # bias toward the top, where subjects usually are
    return img.crop((left, top, left + W, top + H))


def card(slug, src, out):
    s = STORIES[slug]
    base = cover(Image.open(src).convert("RGB"))

    # Dark fade over the lower part so white text stays readable on any photo.
    fade = Image.new("L", (1, H))
    for y in range(H):
        t = max(0.0, (y - H * 0.30) / (H * 0.55))
        fade.putpixel((0, y), int(min(1.0, t) * 235))
    black = Image.new("RGB", (W, H), (0, 0, 0))
    base = Image.composite(black, base, fade.resize((W, H)))
    d = ImageDraw.Draw(base)

    # Headline: shrink until it fits in at most 6 lines.
    for size in range(72, 40, -4):
        hf = font("ariblk.ttf", size)
        lines = wrap(d, s["headline"], hf, W - 2 * PAD)
        if len(lines) <= 6:
            break
    lh = int(size * 1.18)
    credit_f = font("arial.ttf", 22)
    credit = f"Photo: {s['img']['author']} / {s['img']['license']}, Wikimedia Commons. Illustrative."
    credit_lines = wrap(d, credit, credit_f, W - 2 * PAD)
    y = H - PAD - 30 * len(credit_lines) - 24 - lh * len(lines)

    # Brand tag above the headline.
    tf = font("ariblk.ttf", 30)
    tag = "RETARDED NEWS"
    tw = d.textlength(tag, font=tf)
    ty = y - 78
    d.rectangle([PAD, ty, PAD + tw + 36, ty + 52], fill=RED)
    d.text((PAD + 18, ty + 26), tag, font=tf, fill="white", anchor="lm")

    for line in lines:
        d.text((PAD, y), line, font=hf, fill="white")
        y += lh
    y += 24
    for line in credit_lines:
        d.text((PAD, y), line, font=credit_f, fill=(190, 190, 190))
        y += 30
    base.save(out, quality=90)


if __name__ == "__main__":
    src_dir, out_dir, *slugs = sys.argv[1:]
    os.makedirs(out_dir, exist_ok=True)
    slugs = slugs or [f[:-4] for f in os.listdir(src_dir) if f.endswith(".jpg")]
    for slug in slugs:
        card(slug, os.path.join(src_dir, slug + ".jpg"), os.path.join(out_dir, slug + ".jpg"))
    print(f"{len(slugs)} cards")
