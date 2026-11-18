"""Builds the static site from tools/stories.json.

Usage:  python tools/build.py
Writes index.html, one page per category, news/<slug>.html and credits.html.
"""
import html
import json
import os
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
STORIES = json.load(open(os.path.join(ROOT, "tools", "stories.json"), encoding="utf-8"))

CATS = [
    ("index", "Home"), ("world", "World"), ("politics", "Politics"), ("business", "Business"),
    ("tech", "Tech"), ("science", "Science"), ("sports", "Sports"), ("culture", "Culture"),
]
CATNAME = dict(CATS)
SITE = "RetardedNews"
TODAY = "Wednesday, November 18, 2026"

e = html.escape


def fmt_date(iso):
    d = date.fromisoformat(iso)
    return d.strftime("%B %d, %Y").replace(" 0", " ")


def img_src(img, width):
    base = img["url"].split("?")[0]
    return f"{base}?width={width}"


def credit(img, prefix):
    lic = e(img["license"])
    if img.get("license_url"):
        lic = f'<a href="{e(img["license_url"])}" rel="license noopener" target="_blank">{lic}</a>'
    file_page = "https://commons.wikimedia.org/wiki/" + img["file"].replace(" ", "_")
    return (f'Photo: <a href="{e(file_page)}" target="_blank" rel="noopener">{e(img["author"])}</a>'
            f' via Wikimedia Commons, {lic}. Illustrative image, not from the event.')


def page(title, active, body, prefix="", desc=""):
    nav = "\n".join(
        f'      <li><a href="{prefix}{s}.html"{" class=\"active\"" if s == active else ""}>{n}</a></li>'
        for s, n in CATS)
    ticks = "".join(
        f'<a href="{prefix}news/{s["slug"]}.html"><span>{e(s["headline"])}</span></a>' for s in STORIES[:8])
    foot = "".join(f'<a href="{prefix}{s}.html">{n}</a>' for s, n in CATS[1:])
    return f"""<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8">
  <meta name="viewport" content="width=device-width, initial-scale=1">
  <title>{e(title)}</title>
  <meta name="description" content="{e(desc or 'The dumbest, funniest, most unbelievable true news on the internet.')}">
  <link rel="preconnect" href="https://fonts.googleapis.com">
  <link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
  <link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;600;700&family=Playfair+Display:ital,wght@0,700;0,900;1,400&display=swap" rel="stylesheet">
  <link rel="stylesheet" href="{prefix}css/style.css">
</head>
<body id="top">
  <div class="topbar"><div class="wrap"><span>{TODAY}</span><span>Real news. Really dumb.</span></div></div>
  <header class="masthead wrap">
    <a href="{prefix}index.html" class="logo">Retarded<span>News</span></a>
    <p class="tagline">True stories you will not believe, every single day.</p>
  </header>
  <nav class="catnav" aria-label="Categories">
    <ul>
{nav}
    </ul>
  </nav>
  <div class="ticker">
    <div class="ticker-label">Breaking</div>
    <div class="ticker-track"><div class="ticker-items">{ticks}{ticks}</div></div>
  </div>
  <main class="wrap">
{body}
  </main>
  <footer class="footer">
    <div class="wrap">
      <a href="{prefix}index.html" class="logo">Retarded<span>News</span></a>
      <nav>{foot}<a href="{prefix}credits.html">Image credits</a></nav>
      <span>© 2026 {SITE}. Stories rewritten from real reporting; sources linked on every page.</span>
    </div>
  </footer>
  <a class="to-top" href="#top" aria-label="Back to top">↑</a>
</body>
</html>
"""


def meta(s):
    return f'<div class="meta">{fmt_date(s["date"])} · {e(s["location"])} · {s["read"]} min read</div>'


def card(s, prefix="", wide=False):
    href = f'{prefix}news/{s["slug"]}.html'
    w = 900 if wide else 800
    return f"""      <article class="card{' wide' if wide else ''}">
        <a class="thumb" href="{href}"><img src="{img_src(s['img'], w)}" alt="{e(s['img']['alt'])}" loading="lazy"></a>
        <div>
          <a class="tag" href="{prefix}{s['cat']}.html">{CATNAME[s['cat']]}</a>
          <a href="{href}"><h3>{e(s['headline'])}</h3></a>
          <p>{e(s['dek'])}</p>
          {meta(s)}
        </div>
      </article>"""


def lead(main, side, prefix=""):
    side_html = "\n".join(f"""      <article>
        <a href="{prefix}news/{s['slug']}.html"><img src="{img_src(s['img'], 640)}" alt="{e(s['img']['alt'])}" loading="lazy"></a>
        <a class="tag" href="{prefix}{s['cat']}.html">{CATNAME[s['cat']]}</a>
        <a href="{prefix}news/{s['slug']}.html"><h3>{e(s['headline'])}</h3></a>
      </article>""" for s in side)
    href = f'{prefix}news/{main["slug"]}.html'
    return f"""    <section class="lead">
      <article class="lead-main">
        <a href="{href}"><img src="{img_src(main['img'], 1280)}" alt="{e(main['img']['alt'])}"></a>
        <a class="tag" href="{prefix}{main['cat']}.html">{CATNAME[main['cat']]}</a>
        <a href="{href}"><h1>{e(main['headline'])}</h1></a>
        <p>{e(main['dek'])}</p>
        {meta(main)}
      </article>
      {'<aside class="lead-side">' + chr(10) + side_html + chr(10) + '      </aside>' if side else ''}
    </section>
"""


def feed(items, prefix=""):
    cards = [card(s, prefix, wide=(i % 7 == 0 and len(items) > 2)) for i, s in enumerate(items)]
    return '    <section class="feed">\n' + "\n".join(cards) + "\n    </section>\n"


def head(title, sub):
    return f'    <div class="section-head"><h2>{e(title)}</h2><p>{sub}</p></div>\n'


def figure(img, cls=""):
    return f"""      <figure class="figure {cls}">
        <img src="{img_src(img, 1600 if cls == 'hero' else 1200)}" alt="{e(img['alt'])}">
        <figcaption>{credit(img, '')}</figcaption>
      </figure>"""


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
    more = [o for o in STORIES if o["slug"] != s["slug"] and o["cat"] == s["cat"]]
    more += [o for o in STORIES if o["slug"] != s["slug"] and o not in more]
    body = f"""    <article class="article">
      <header class="article-head">
        <a class="tag" href="../{s['cat']}.html">{CATNAME[s['cat']]}</a>
        <h1>{e(s['headline'])}</h1>
        <p class="dek">{e(s['dek'])}</p>
        <div class="byline">By <b>{SITE} Staff</b> · {fmt_date(s['date'])} · {e(s['location'])} · {s['read']} min read</div>
      </header>
{figure(s['img'], 'hero')}
      <div class="article-body">
{chr(10).join(parts)}
      </div>
      <aside class="sources">
        <h4>Original reporting</h4>
        <ul>{sources}</ul>
      </aside>
      <p class="disclaimer">This story is a humorous rewrite of real news reports. Facts come from the sources above; any jokes are ours.</p>
    </article>
{head('More dumb news', '<a href="../index.html">All stories →</a>')}{feed(more[:6], '../')}"""
    return page(f"{s['headline']} — {SITE}", s["cat"], body, "../", s["dek"])


def build():
    os.makedirs(os.path.join(ROOT, "news"), exist_ok=True)
    out = {}

    # Homepage: top story, three side stories, then everything else.
    body = lead(STORIES[0], STORIES[1:4])
    body += head("Latest stupidity", f"{len(STORIES)} true stories")
    body += feed(STORIES[4:])
    out["index.html"] = page(SITE, "index", body)

    # Category pages.
    for slug, name in CATS[1:]:
        mine = [s for s in STORIES if s["cat"] == slug]
        others = [s for s in STORIES if s["cat"] != slug]
        if mine:
            body = lead(mine[0], mine[1:4])
            if mine[4:]:
                body += head(f"More {name}", f"{len(mine)} stories") + feed(mine[4:])
        else:
            body = head(name, "Nothing dumb enough here yet")
        body += head("Elsewhere on " + SITE, '<a href="index.html">All stories →</a>') + feed(others[:6])
        out[f"{slug}.html"] = page(f"{name} — {SITE}", slug, body)

    # Article pages.
    for s in STORIES:
        out[f"news/{s['slug']}.html"] = article_page(s)

    # Credits.
    rows = []
    for s in STORIES:
        for img in filter(None, [s["img"], s.get("img2")]):
            rows.append(f'      <li><a href="news/{s["slug"]}.html">{e(s["headline"])}</a> — {credit(img, "")}</li>')
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
