"""Builds 1200x630 share cards: the story's website photo with its one-line hook on top.

Usage:  python tools/make_cards.py SRC_DIR [slug ...]
SRC_DIR holds <slug>.jpg source photos (the story's Commons image). Cards go to cards/<slug>.jpg,
which build.py uses as each article's og:image, so Facebook link posts show the card.
"""
import json
import os
import sys

from PIL import Image, ImageDraw, ImageFont

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORIES = {s["slug"]: s for s in json.load(open(os.path.join(ROOT, "tools", "stories.json"), encoding="utf-8"))}
OUT = os.path.join(ROOT, "cards")
F = "C:/Windows/Fonts/"
W, H = 1200, 630
RED = (200, 16, 46)
PAD = 48


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


def shade(base):
    """Dark fade at the top (hook) and a lighter one at the bottom (tag and credit)."""
    mask = Image.new("L", (1, H))
    for y in range(H):
        top = max(0.0, 1 - y / (H * 0.55)) * 215
        bottom = max(0.0, (y - H * 0.78) / (H * 0.22)) * 170
        mask.putpixel((0, y), int(max(top, bottom)))
    return Image.composite(Image.new("RGB", (W, H)), base, mask.resize((W, H)))


def card(slug, src):
    s = STORIES[slug]
    base = shade(cover(Image.open(src).convert("RGB")))
    d = ImageDraw.Draw(base)

    for size in range(66, 38, -2):  # largest size that fits in two lines
        hf = font("ariblk.ttf", size)
        lines = wrap(d, s["hook"], hf, W - 2 * PAD)
        if len(lines) <= 2:
            break
    y = PAD - 6
    for line in lines:
        d.text((PAD + 3, y + 3), line, font=hf, fill=(0, 0, 0))  # soft drop shadow
        d.text((PAD, y), line, font=hf, fill="white")
        y += int(size * 1.2)

    tf = font("ariblk.ttf", 24)
    tag = "RETARDED NEWS"
    tw = d.textlength(tag, font=tf)
    d.rectangle([PAD, H - PAD - 42, PAD + tw + 28, H - PAD], fill=RED)
    d.text((PAD + 14, H - PAD - 21), tag, font=tf, fill="white", anchor="lm")

    cf = font("arial.ttf", 16)
    credit = f"Photo: {s['img']['author']} / {s['img']['license']}, Wikimedia Commons (illustrative)"
    while d.textlength(credit, font=cf) > W - 2 * PAD - tw - 60:
        credit = credit[:-2]
    d.text((W - PAD, H - PAD - 21), credit, font=cf, fill=(215, 215, 215), anchor="rm")
    base.save(os.path.join(OUT, slug + ".jpg"), quality=88)


if __name__ == "__main__":
    src_dir, *slugs = sys.argv[1:]
    os.makedirs(OUT, exist_ok=True)
    slugs = slugs or [f[:-4] for f in os.listdir(src_dir) if f.endswith(".jpg") and f[:-4] in STORIES]
    for slug in slugs:
        card(slug, os.path.join(src_dir, slug + ".jpg"))
    print(f"{len(slugs)} cards")
