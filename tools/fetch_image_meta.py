"""Caches original pixel sizes of every Commons image in stories.json.

Usage:  python tools/fetch_image_meta.py
Writes tools/image_meta.json ({"File:Name.jpg": [width, height]}), which
build.py uses to link Wikimedia thumbnails directly and set width/height.
Re-run after adding stories with new images.
"""
import json
import os
import urllib.parse
import urllib.request

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORIES = json.load(open(os.path.join(ROOT, "tools", "stories.json"), encoding="utf-8"))
OUT = os.path.join(ROOT, "tools", "image_meta.json")


def main():
    meta = json.load(open(OUT, encoding="utf-8")) if os.path.exists(OUT) else {}
    files = sorted({img["file"] for s in STORIES for img in (s["img"], s.get("img2")) if img})
    todo = [f for f in files if f not in meta]
    for i in range(0, len(todo), 40):
        chunk = todo[i:i + 40]
        q = urllib.parse.urlencode({"action": "query", "format": "json", "prop": "imageinfo",
                                    "iiprop": "size", "titles": "|".join(chunk)})
        req = urllib.request.Request("https://commons.wikimedia.org/w/api.php?" + q,
                                     headers={"User-Agent": "static-site-build/1.0"})
        data = json.load(urllib.request.urlopen(req, timeout=30))
        norm = {n["to"]: n["from"] for n in data["query"].get("normalized", [])}
        for p in data["query"]["pages"].values():
            if "imageinfo" not in p:
                print("missing:", p.get("title"))
                continue
            ii = p["imageinfo"][0]
            meta[norm.get(p["title"], p["title"])] = [ii["width"], ii["height"]]
    with open(OUT, "w", encoding="utf-8", newline="\n") as f:
        json.dump(meta, f, indent=1, sort_keys=True, ensure_ascii=False)
    print(f"{len(meta)} images cached, {len(todo)} fetched")


if __name__ == "__main__":
    main()
