import sys
from PIL import Image, ImageDraw, ImageFont
out = sys.argv[1]
RED=(200,16,46); CREAM=(247,245,240); INK=(22,21,15)
F="C:/Windows/Fonts/"
bold=lambda s: ImageFont.truetype(F+"georgiab.ttf", s)
ital=lambda s: ImageFont.truetype(F+"georgiai.ttf", s)

def profile(S=2048):
    im=Image.new("RGB",(S,S),RED)
    L=Image.new("RGBA",(S,S),(0,0,0,0)); ld=ImageDraw.Draw(L)
    f=bold(int(S*.36)); sf=bold(int(S*.075))
    wR=ld.textlength("R",font=f); wN=ld.textlength("N",font=f)
    ov=S*.045; total=wR+wN-ov
    cap=ld.textbbox((0,0),"N",font=f,anchor="ls")[1]*-1   # cap height
    ncap=-ld.textbbox((0,0),"NEWS",font=sf,anchor="ls")[1]
    lw=int(S*.011); gap=S*.035
    # stack: rule, RN, rule, NEWS
    h=3*lw+gap+cap+gap+3*lw+gap+ncap
    top=(S-h)/2
    rx0=(S-total)/2-S*.01; rx1=rx0+total+S*.02
    y=top
    ld.rectangle([rx0,y,rx1,y+2*lw],fill=CREAM); ld.rectangle([rx0,y+2.6*lw,rx1,y+3.4*lw],fill=CREAM)
    y+=3.4*lw+gap+cap
    x=(S-total)/2
    ld.text((x,y),"R",font=f,fill=CREAM,anchor="ls")
    ld.text((x+wR-ov,y),"N",font=f,fill=INK,anchor="ls")
    y+=gap
    ld.rectangle([rx0,y,rx1,y+.8*lw],fill=CREAM); ld.rectangle([rx0,y+1.4*lw,rx1,y+3.4*lw],fill=CREAM)
    y+=3.4*lw+gap+ncap
    ld.text((S/2,y),"N E W S",font=sf,fill=CREAM,anchor="ms")
    L=L.rotate(4,resample=Image.BICUBIC,center=(S/2,S/2))
    im.paste(L,(0,0),L)
    # circle-crop preview
    m=Image.new("L",(S,S),0); ImageDraw.Draw(m).ellipse([0,0,S,S],fill=255)
    pv=Image.new("RGB",(S,S),(36,37,38)); pv.paste(im,(0,0),m)
    pv.resize((512,512),Image.LANCZOS).save(out+"/_preview-circle.png")
    im.resize((1024,1024),Image.LANCZOS).save(out+"/profile-1024.png")
    im.resize((180,180),Image.LANCZOS).save(out+"/favicon-180.png")
    im.resize((32,32),Image.LANCZOS).save(out+"/favicon-32.png")

def cover(W=3280,H=1248):
    im=Image.new("RGB",(W,H),CREAM); d=ImageDraw.Draw(im)
    f=bold(int(H*.24)); w1=d.textlength("Retarded",font=f); w2=d.textlength("News",font=f)
    x=(W-(w1+w2))/2; y=H*.53
    d.text((x,y),"Retarded",font=f,fill=INK,anchor="ls")
    d.text((x+w1,y),"News",font=f,fill=RED,anchor="ls")
    lw=int(H*.008); x0=W*.2; x1=W*.8
    d.rectangle([x0,H*.25,x1,H*.25+lw*2],fill=INK); d.rectangle([x0,H*.27,x1,H*.27+lw],fill=INK)
    d.rectangle([x0,H*.62,x1,H*.62+lw],fill=INK); d.rectangle([x0,H*.64,x1,H*.64+lw*2],fill=INK)
    d.text((W/2,H*.75),"True stories you will not believe, every single day.",font=ital(int(H*.055)),fill=(107,103,92),anchor="ms")
    im.resize((1640,624),Image.LANCZOS).save(out+"/cover-1640x624.png")
profile(); cover()
