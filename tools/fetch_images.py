"""Downloads every story image into img/ so the site never hotlinks Wikimedia.

Usage:  python tools/fetch_images.py [--force]
Run after tools/fetch_image_meta.py and before tools/build.py.

Rule: all images are self-hosted. Facebook's crawler gets 403 from upload.wikimedia.org,
and hotlinked images can vanish or be rate-limited. build.py refuses to build if a file is missing.

For each Commons image it saves img/<key>-<width>.jpg at every srcset width build.py uses
(key = build.img_key). It also writes img/og/<slug>.jpg (1200x630, Facebook's 1.91:1 ratio)
for each story's hero image, used as og:image unless cards/<slug>.jpg exists.
Existing files are skipped unless --force is given.
"""
import io
import os
import sys
import time
import urllib.error
import urllib.request

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import build  # noqa: E402

IMG_DIR = os.path.join(build.ROOT, "img")
OG_DIR = os.path.join(IMG_DIR, "og")
OG_W, OG_H = 1200, 630


def fetch(url):
    """Polite download: pauses between files and backs off on 429 (Wikimedia rate limit)."""
    req = urllib.request.Request(url, headers={"User-Agent": "RetardedNewsCardBuilder/1.0 (https://retardednews.github.io/)"})
    for attempt in range(10):
        time.sleep(1.5)
        try:
            data = urllib.request.urlopen(req, timeout=60).read()
            break
        except urllib.error.HTTPError as err:
            if err.code != 429 or attempt == 9:
                raise
            wait = int(err.headers.get("Retry-After") or 0) or 30 * (attempt + 1)
            print(f"rate limited, waiting {wait}s")
            time.sleep(wait)
    im = Image.open(io.BytesIO(data))
    if im.mode in ("RGBA", "LA", "P"):
        im = im.convert("RGBA")
        bg = Image.new("RGB", im.size, (255, 255, 255))
        bg.paste(im, mask=im.split()[-1])
        return bg
    return im.convert("RGB")


def save(im, path):
    im.save(path, "JPEG", quality=84, optimize=True, progressive=True)
    print("saved", os.path.relpath(path, build.ROOT))


def resize(im, w):
    return im if im.width == w else im.resize((w, round(im.height * w / im.width)), Image.LANCZOS)


def og_crop(im):
    scale = max(OG_W / im.width, OG_H / im.height)
    im = im.resize((round(im.width * scale), round(im.height * scale)), Image.LANCZOS)
    left, top = (im.width - OG_W) // 2, (im.height - OG_H) // 2
    return im.crop((left, top, left + OG_W, top + OG_H))


def main():
    force = "--force" in sys.argv
    os.makedirs(OG_DIR, exist_ok=True)
    missing = {img["file"] for s in build.STORIES for img in (s["img"], s.get("img2")) if img} - set(build.IMG_META)
    if missing:
        sys.exit("Run tools/fetch_image_meta.py first; no size data for: " + ", ".join(sorted(missing)))

    hero_of = {}  # Commons file -> slugs that use it as hero (for og crops)
    for s in build.STORIES:
        if not os.path.exists(os.path.join(build.ROOT, "cards", s["slug"] + ".jpg")):  # custom share card wins
            hero_of.setdefault(s["img"]["file"], []).append(s["slug"])
    seen = {}
    for s in build.STORIES:
        for img in filter(None, (s["img"], s.get("img2"))):
            seen[img["file"]] = img

    for file, img in seen.items():
        widths = build.local_widths(img)
        paths = {w: os.path.join(build.ROOT, build.local_src(img, w)) for w in widths}
        ogs = [os.path.join(OG_DIR, slug + ".jpg") for slug in hero_of.get(file, [])]
        todo = [p for p in list(paths.values()) + ogs if force or not os.path.exists(p)]
        if not todo:
            continue
        src = fetch(build._thumb(img, 10**9))  # original file: thumbnail renders are rate-limited far harder
        for w, p in paths.items():
            if p in todo:
                save(resize(src, w), p)
        for p in ogs:
            if p in todo:
                save(og_crop(src), p)


if __name__ == "__main__":
    main()
