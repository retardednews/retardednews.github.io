"""Builds the static site from tools/stories.json.

Usage:  python tools/build.py
Writes index.html, one page per category, news/<slug>.html and credits.html.
Image sizes come from tools/image_meta.json (refresh with tools/fetch_image_meta.py).
"""
import hashlib
import html
import json
import os
import urllib.parse
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORIES = json.load(open(os.path.join(ROOT, "tools", "stories.json"), encoding="utf-8"))
META_PATH = os.path.join(ROOT, "tools", "image_meta.json")
IMG_META = json.load(open(META_PATH, encoding="utf-8")) if os.path.exists(META_PATH) else {}

CATS = [
    ("index", "Home"), ("world", "World"), ("politics", "Politics"), ("business", "Business"),
    ("tech", "Tech"), ("science", "Science"), ("sports", "Sports"), ("culture", "Culture"),
]
CATNAME = dict(CATS)
SITE = "RetardedNews"
YEAR = date.today().year

# Wikimedia only serves thumbnails at these standard widths; anything else is rejected.
THUMB_WIDTHS = [330, 500, 960, 1280, 1920]

e = html.escape


def by_date(items):
    return sorted(items, key=lambda s: s["date"], reverse=True)


def fmt_date(iso):
    d = date.fromisoformat(iso)
    return d.strftime("%B %d, %Y").replace(" 0", " ")


def short_place(loc):
    """'Lehi, Utah to Jurupa Valley, California, USA' -> 'Lehi → Jurupa Valley'."""
    sides = loc.split(" to ")
    if len(sides) > 1:
        return " → ".join(side.split(",")[0].strip() for side in sides)
    parts = [p.strip() for p in loc.split(",")]
    return parts[0] if len(parts) == 1 else f"{parts[0]}, {parts[-1]}"


# ---------- Images ----------

def _commons_name(img):
    return img["file"].split(":", 1)[1].replace(" ", "_")


def _thumb(img, width):
    """Direct upload.wikimedia.org URL (no Special:FilePath redirect hops)."""
    name = _commons_name(img)
    h = hashlib.md5(name.encode("utf-8")).hexdigest()
    q = urllib.parse.quote(name)
    orig_w = IMG_META[img["file"]][0]
    if width >= orig_w:
        return f"https://upload.wikimedia.org/wikipedia/commons/{h[0]}/{h[:2]}/{q}"
    return f"https://upload.wikimedia.org/wikipedia/commons/thumb/{h[0]}/{h[:2]}/{q}/{width}px-{q}"


def img_tag(img, sizes, max_w=1280, eager=False):
    """<img> with srcset, intrinsic width/height (stops layout shift) and lazy loading."""
    alt = e(img["alt"])
    load = ' fetchpriority="high"' if eager else ' loading="lazy" decoding="async"'
    if img["file"] not in IMG_META:  # fall back to the redirecting URL if sizes are not cached
        base = img["url"].split("?")[0]
        return f'<img src="{base}?width={max_w}" alt="{alt}"{load}>'
    ow, oh = IMG_META[img["file"]]
    widths = [w for w in THUMB_WIDTHS if w < ow and w <= max_w] or [ow]
    if max_w >= ow and ow not in widths:
        widths.append(ow)
    srcset = ", ".join(f"{e(_thumb(img, w))} {w}w" for w in widths)
    w = widths[-1]
    hgt = round(oh * w / ow)
    return (f'<img src="{e(_thumb(img, w))}" srcset="{srcset}" sizes="{sizes}" '
            f'width="{w}" height="{hgt}" alt="{alt}"{load}>')


def credit(img):
    lic = e(img["license"])
    if img.get("license_url"):
        lic = f'<a href="{e(img["license_url"])}" rel="license noopener" target="_blank">{lic}</a>'
    file_page = "https://commons.wikimedia.org/wiki/" + img["file"].replace(" ", "_")
    return (f'Photo: <a href="{e(file_page)}" target="_blank" rel="noopener">{e(img["author"])}</a>'
            f' via Wikimedia Commons, {lic}. Illustrative image, not from the event.')


# ---------- Page shell ----------

THEME_BOOT = ("<script>try{var t=localStorage.getItem('theme');"
              "if(t)document.documentElement.dataset.theme=t}catch(e){}</script>")


def page(title, active, body, prefix="", desc=""):
    nav = "\n".join(
        f'        <li><a href="{prefix}{s}.html"{" class=\"active\" aria-current=\"page\"" if s == active else ""}>{n}</a></li>'
        for s, n in CATS)
    foot = "".join(f'<a href="{prefix}{s}.html">{n}</a>' for s, n in CATS[1:])
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(title)}</title>
  <meta name="description" content="{e(desc or 'The dumbest, funniest, most unbelievable true news on the internet.')}">
  {THEME_BOOT}
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link rel="preconnect" href="https://upload.wikimedia.org">
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Playfair+Display:ital,wght@0,700;0,900;1,400&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{prefix}css/style.css">
  <script src="{prefix}js/site.js" defer></script>
</head>
<body id="top">
  <div class="topbar"><div class="wrap"><span id="today"></span><span>Real news. As dumb as it gets.</span></div></div>
  <header class="masthead wrap">
    <a href="{prefix}index.html" class="logo">Retarded<span>News</span></a>
    <p class="tagline">True stories you will not believe, every single day.</p>
  </header>
  <nav class="catnav" aria-label="Categories">
    <div class="catnav-inner">
      <a href="{prefix}index.html" class="catnav-logo" aria-label="{SITE} home" tabindex="-1">R<span>N</span></a>
      <ul>
{nav}
      </ul>
      <button class="theme-toggle" type="button" aria-label="Toggle dark mode" title="Toggle dark mode">
        <svg viewBox="0 0 24 24" width="18" height="18" aria-hidden="true"><path fill="currentColor" d="M12 3a9 9 0 1 0 9 9c0-.46-.04-.92-.1-1.36a5.39 5.39 0 0 1-4.4 2.26 5.4 5.4 0 0 1-3.14-9.8C12.92 3.04 12.46 3 12 3z"/></svg>
      </button>
    </div>
  </nav>
  <main class="wrap">
{body}
  </main>
  <footer class="footer">
    <div class="wrap">
      <a href="{prefix}index.html" class="logo">Retarded<span>News</span></a>
      <nav aria-label="Footer">{foot}<a href="{prefix}credits.html">Image credits</a></nav>
      <span>© {YEAR} {SITE}. Stories rewritten from real reporting; sources linked on every page.</span>
    </div>
  </footer>
  <a class="to-top" href="#top" aria-label="Back to top">↑</a>
</body>
</html>
"""


# ---------- Building blocks ----------

def meta(s, short=True):
    place = short_place(s["location"]) if short else s["location"]
    return (f'<div class="meta"><time datetime="{s["date"]}">{fmt_date(s["date"])}</time>'
            f' · {e(place)} · {s["read"]} min read</div>')


def tag(s, prefix):
    return f'<a class="tag" href="{prefix}{s["cat"]}.html">{CATNAME[s["cat"]]}</a>'


def card(s, prefix="", wide=False):
    """Whole card is one link (the headline's ::after covers it); the tag stays separately clickable."""
    href = f'{prefix}news/{s["slug"]}.html'
    sizes = "(max-width: 640px) 100vw, (max-width: 960px) 50vw, 760px" if wide else \
            "(max-width: 640px) 100vw, (max-width: 960px) 50vw, 380px"
    return f"""      <article class="card{' wide' if wide else ''}">
        <div class="thumb">{img_tag(s['img'], sizes, 1280 if wide else 960)}</div>
        <div class="card-body">
          {tag(s, prefix)}
          <h3><a class="card-link" href="{href}">{e(s['headline'])}</a></h3>
          <p>{e(s['dek'])}</p>
          {meta(s)}
        </div>
      </article>"""


def lead(main, side, prefix="", hl="h1"):
    side_html = "\n".join(f"""      <article class="card">
        <div class="thumb">{img_tag(s['img'], "(max-width: 640px) 100vw, (max-width: 960px) 33vw, 400px", 960)}</div>
        {tag(s, prefix)}
        <h3><a class="card-link" href="{prefix}news/{s['slug']}.html">{e(s['headline'])}</a></h3>
      </article>""" for s in side)
    href = f'{prefix}news/{main["slug"]}.html'
    aside = f'<aside class="lead-side lead-side-{len(side)}">\n{side_html}\n      </aside>' if side else ""
    return f"""    <section class="lead{'' if side else ' lead-solo'}">
      <article class="lead-main card">
        <div class="thumb">{img_tag(main['img'], "(max-width: 960px) 100vw, 740px", 1280, eager=True)}</div>
        {tag(main, prefix)}
        <{hl}><a class="card-link" href="{href}">{e(main['headline'])}</a></{hl}>
        <p>{e(main['dek'])}</p>
        {meta(main)}
      </article>
      {aside}
    </section>
"""


def feed(items, prefix=""):
    cards = [card(s, prefix, wide=(i % 7 == 0 and len(items) > 2)) for i, s in enumerate(items)]
    return '    <section class="feed">\n' + "\n".join(cards) + "\n    </section>\n"


def head(title, sub, level="h2"):
    return f'    <div class="section-head"><{level}>{e(title)}</{level}><p>{sub}</p></div>\n'


def figure(img, cls=""):
    hero = cls == "hero"
    sizes = "(max-width: 860px) 100vw, 760px" if hero else "(max-width: 720px) 100vw, 680px"
    return f"""      <figure class="figure {cls}">
        {img_tag(img, sizes, 1280, eager=hero)}
        <figcaption>{credit(img)}</figcaption>
      </figure>"""


def pager(s):
    i = STORIES.index(s)
    prev_s = STORIES[i - 1] if i > 0 else None
    next_s = STORIES[i + 1] if i + 1 < len(STORIES) else None
    cell = lambda o, label, cls: (
        f'<a class="pager-{cls}" href="{o["slug"]}.html"><span>{label}</span>{e(o["headline"])}</a>'
        if o else '<span></span>')
    return (f'      <nav class="pager" aria-label="More stories">{cell(prev_s, "← Previous story", "prev")}'
            f'{cell(next_s, "Next story →", "next")}</nav>')


def article_page(s):
    parts = []
    for block in s["body"]:
        if isinstance(block, str):
            parts.append(f"        <p>{e(block)}</p>")
        elif "quote" in block:
            parts.append(f'        <blockquote class="pullquote">{e(block["quote"])}</blockquote>')
        elif "h2" in block:
            parts.append(f"        <h2>{e(block['h2'])}</h2>")
        elif "img2" in block and s.get("img2"):
            parts.append(figure(s["img2"]))
    sources = "".join(
        f'<li><a href="{e(src["url"])}" target="_blank" rel="noopener">{e(src["name"])}</a></li>'
        for src in s["sources"])
    same = by_date(o for o in STORIES if o["slug"] != s["slug"] and o["cat"] == s["cat"])
    rest = by_date(o for o in STORIES if o["slug"] != s["slug"] and o["cat"] != s["cat"])
    more = (same + rest)[:6]
    more_title = f"More {CATNAME[s['cat']]}" if same else "More dumb news"
    body = f"""    <article class="article">
      <header class="article-head">
        {tag(s, '../')}
        <h1>{e(s['headline'])}</h1>
        <p class="dek">{e(s['dek'])}</p>
        <div class="byline">By <b>{SITE} Staff</b> · <time datetime="{s['date']}">{fmt_date(s['date'])}</time> · {e(s['location'])} · {s['read']} min read</div>
      </header>
{figure(s['img'], 'hero')}
      <div class="article-body">
{chr(10).join(parts)}
      </div>
      <aside class="sources">
        <h2>Original reporting</h2>
        <ul>{sources}</ul>
      </aside>
      <p class="disclaimer">This story is a humorous rewrite of real news reports. Facts come from the sources above; any jokes are ours.</p>
{pager(s)}
    </article>
{head(more_title, '<a href="../index.html">All stories →</a>')}{feed(more, '../')}"""
    return page(f"{s['headline']} — {SITE}", s["cat"], body, "../", s["dek"])


def build():
    os.makedirs(os.path.join(ROOT, "news"), exist_ok=True)
    missing = {img["file"] for s in STORIES for img in (s["img"], s.get("img2")) if img} - set(IMG_META)
    if missing:
        print(f"warning: {len(missing)} images lack cached sizes; run tools/fetch_image_meta.py")
    out = {}

    # Homepage: curated top story and three side stories, then everything else newest first.
    body = lead(STORIES[0], STORIES[1:4])
    body += head("Latest stupidity", f"{len(STORIES)} true stories, newest first")
    body += feed(by_date(STORIES[4:]))
    out["index.html"] = page(SITE, "index", body)

    # Category pages: only that category's stories, then a clearly separate "elsewhere" block.
    for slug, name in CATS[1:]:
        mine = by_date(s for s in STORIES if s["cat"] == slug)
        others = by_date(s for s in STORIES if s["cat"] != slug)
        count = f"{len(mine)} {'story' if len(mine) == 1 else 'stories'}"
        if mine:
            body = head(name, count, "h1")
            side = mine[1:4] if len(mine) >= 3 else []
            body += lead(mine[0], side, hl="h2")
            rest = mine[1 + len(side):]
            if rest:
                body += head(f"More {name}", "") + feed(rest)
        else:
            body = head(name, "0 stories", "h1")
            body += ('    <p class="empty">Nothing dumb enough has happened in '
                     f'{e(name)} yet. Give it a week.</p>\n')
        body += head("Elsewhere on " + SITE, '<a href="index.html">All stories →</a>') + feed(others[:6])
        out[f"{slug}.html"] = page(f"{name} — {SITE}", slug, body)

    # Article pages.
    for s in STORIES:
        out[f"news/{s['slug']}.html"] = article_page(s)

    # Credits.
    rows = []
    for s in STORIES:
        for img in filter(None, [s["img"], s.get("img2")]):
            rows.append(f'      <li><a href="news/{s["slug"]}.html">{e(s["headline"])}</a> — {credit(img)}</li>')
    body = f"""    <article class="article">
      <header class="article-head"><h1>Image credits</h1>
        <p class="dek">Every photo on {SITE} comes from Wikimedia Commons under a public-domain or Creative Commons licence. Photos are illustrative and were not taken at the events described.</p>
      </header>
      <div class="sources"><ul>
{chr(10).join(rows)}
      </ul></div>
    </article>
"""
    out["credits.html"] = page(f"Image credits — {SITE}", "", body)

    for name, text in out.items():
        with open(os.path.join(ROOT, name), "w", encoding="utf-8", newline="\n") as f:
            f.write(text)
    print(f"Wrote {len(out)} pages")


if __name__ == "__main__":
    build()
