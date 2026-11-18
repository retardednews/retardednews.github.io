"""Facebook cover for RetardedNews. Usage: python make_cover.py <out_dir>"""
import sys
from PIL import Image, ImageDraw, ImageFont
out = sys.argv[1] if len(sys.argv) > 1 else "brand"
K = 2; W, H = 1640*K, 624*K
RED=(200,16,46); CREAM=(247,245,240); INK=(22,21,15); MUTED=(160,155,142); RULE=(60,57,50)
F="C:/Windows/Fonts/"
def fnt(name, s): return ImageFont.truetype(F+name, int(s*K))
bold=lambda s: fnt("georgiab.ttf", s); ital=lambda s: fnt("georgiai.ttf", s); reg=lambda s: fnt("georgia.ttf", s)

im = Image.new("RGB", (W, H), INK); d = ImageDraw.Draw(im)
def hline(y, x0=0, x1=W, w=1, c=CREAM): d.rectangle([x0, y*K, x1, (y+w)*K-1], fill=c)
cx = W/2

# giant faint watermark
wm = Image.new("RGBA", (W, H), (0,0,0,0)); wd = ImageDraw.Draw(wm)
wd.text((W*0.985, H*1.08), "?!", font=bold(720), fill=(255,255,255,7), anchor="rs")
wd.text((W*0.015, H*1.08), "!?", font=bold(720), fill=(255,255,255,7), anchor="ls")
im.paste(wm, (0,0), wm)

# top strip
hline(18, w=1, c=RULE)
d.text((60*K, 44*K), "VOL. I  ·  NO. 25", font=bold(15), fill=MUTED, anchor="ls")
d.text((W-60*K, 44*K), "EST. 2026", font=bold(15), fill=MUTED, anchor="rs")
d.text((cx, 44*K), "—  EVERY STORY IS REAL. WE CHECKED.  —", font=bold(15), fill=CREAM, anchor="ms")
hline(58, w=1, c=RULE)

# masthead
mf = bold(124); w1 = d.textlength("Retarded", font=mf); w2 = d.textlength("News", font=mf)
x = cx - (w1+w2)/2; base = 214*K
d.text((x, base), "Retarded", font=mf, fill=CREAM, anchor="ls")
d.text((x+w1, base), "News", font=mf, fill=RED, anchor="ls")
mx0, mx1 = x, x+w1+w2
hline(238, mx0, mx1, 4); hline(246, mx0, mx1, 1)
d.text((cx, 298*K), "True stories you will not believe, every single day.", font=ital(24), fill=MUTED, anchor="ms")

# three front-page teasers (kept inside the mobile-safe centre)
cols = [("BUSINESS", "Bank puts $81 trillion", "into the wrong account"),
        ("POLITICS", "Beavers finish 7-year", "dam project overnight"),
        ("SCIENCE", "Orcas start wearing", "dead salmon as hats")]
cw = 330*K; gap = 30*K; total = 3*cw + 2*gap; x0 = cx - total/2
for i, (kick, l1, l2) in enumerate(cols):
    lx = x0 + i*(cw+gap)
    if i: d.rectangle([lx-gap/2, 340*K, lx-gap/2+K-1, 448*K], fill=RULE)
    d.text((lx + cw/2, 362*K), kick, font=bold(14), fill=RED, anchor="ms")
    d.text((lx + cw/2, 400*K), l1, font=bold(25), fill=CREAM, anchor="ms")
    d.text((lx + cw/2, 432*K), l2, font=bold(25), fill=CREAM, anchor="ms")

# breaking ticker
ty0, ty1 = 520*K, 576*K
d.rectangle([0, ty0, W, ty1], fill=RED)
tag = "BREAKING"; tf = bold(22)
tw = d.textlength(tag, font=tf) + 40*K
SAFE = (1640 - int(624*16/9))//2*K + 20*K
d.rectangle([SAFE, ty0, SAFE + tw, ty1], fill=CREAM)
d.text((SAFE + tw/2, (ty0+ty1)/2), tag, font=tf, fill=RED, anchor="mm")
items = ["Raccoon drinks the scotch shelf dry", "Judge rules tacos are sandwiches",
         "12 tonnes of KitKats vanish", "Court: a fart is not free speech",
         "Man paddles a 1,214-lb pumpkin 46 miles", "Otter 841 still at large"]
hf = reg(22); px = SAFE + tw + 30*K; my = (ty0+ty1)/2
for it in items:
    d.text((px, my), it, font=hf, fill=CREAM, anchor="lm")
    px += d.textlength(it, font=hf) + 26*K
    d.ellipse([px-4*K, my-4*K, px+4*K, my+4*K], fill=INK); px += 26*K
hline(600, w=1, c=RULE)

im.resize((1640, 624), Image.LANCZOS).save(f"{out}/cover-1640x624.png")
# crop previews: desktop shows ~1640x624 at 820x312, mobile crops sides to 16:9
mw = int(624*16/9); m = im.resize((1640,624), Image.LANCZOS).crop(((1640-mw)//2, 0, (1640+mw)//2, 624))
m.save(f"{out}/_preview-mobile.png")
