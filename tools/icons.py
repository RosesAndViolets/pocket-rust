"""Draws the app icons (Bubblegum: pink tile, chunky white bubble, grape `rs`)."""
from pathlib import Path
from PIL import Image, ImageDraw, ImageFont
OUT = Path(__file__).resolve().parent.parent / "icons"
FONT = "/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf"
PINK, PLUM, GRAPE, WHITE = "#ffb8d4", "#2a1533", "#8e5cff", "#ffffff"

def draw(size, name, pad=0.2):
    s = 4 * size  # draw large, shrink for smooth edges
    im = Image.new("RGB", (s, s), PINK)
    d = ImageDraw.Draw(im)
    m, w = int(s * pad), int(s * 0.035)
    box = [m, m, s - m, s - m - int(s * 0.04)]
    shadow = [box[0], box[1] + int(s * 0.05), box[2], box[3] + int(s * 0.05)]
    d.rounded_rectangle(shadow, radius=int(s * 0.16), fill=PLUM)
    d.rounded_rectangle(box, radius=int(s * 0.16), fill=WHITE, outline=PLUM, width=w)
    f = ImageFont.truetype(FONT, int(s * 0.27))
    cx, cy = s / 2, (box[1] + box[3]) / 2
    d.text((cx, cy), "rs", font=f, fill=GRAPE, anchor="mm")
    im.resize((size, size), Image.LANCZOS).save(OUT / name)

draw(512, "icon-512.png", pad=0.2)
draw(192, "icon-192.png", pad=0.2)
draw(180, "apple-touch-icon.png", pad=0.14)
draw(512, "maskable-512.png", pad=0.26)
