"""Regenerate the PWA PNG icons from the flame motif (matches icon.svg):
an orange flame on a blue radial background.

Requires Pillow:  pip install Pillow
Run from this folder:  python make_icons.py
"""
import os
from PIL import Image, ImageDraw, ImageFilter

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons")
os.makedirs(OUT, exist_ok=True)
SS = 4  # supersample for clean edges

BG    = (0x1A, 0x2A, 0x6C)   # dark blue background
FLAME = (0xFF, 0x8A, 0x2E)   # the orange flame
CORE  = (0xFF, 0xE9, 0xC8)   # warm core
GLOW  = (0xFF, 0x8A, 0x2E)   # the light it throws
SCALE = 2.28                 # enlarge the flame to ~90% of the icon (10% margin)

def cubic(p0, p1, p2, p3, n=40):
    out = []
    for i in range(n + 1):
        t = i / n; u = 1 - t
        x = u*u*u*p0[0] + 3*u*u*t*p1[0] + 3*u*t*t*p2[0] + t*t*t*p3[0]
        y = u*u*u*p0[1] + 3*u*u*t*p1[1] + 3*u*t*t*p2[1] + t*t*t*p3[1]
        out.append((x, y))
    return out

# flame + inner core outlines in 512-space (matches icon.svg)
flame512 = (cubic((256,150),(300,198),(318,232),(318,274))
          + cubic((318,274),(318,320),(290,352),(256,352))
          + cubic((256,352),(222,352),(194,320),(194,274))
          + cubic((194,274),(194,232),(212,198),(256,150)))
core512  = (cubic((256,232),(274,254),(282,272),(282,292))
          + cubic((282,292),(282,314),(271,330),(256,330))
          + cubic((256,330),(241,330),(230,314),(230,292))
          + cubic((230,292),(230,272),(238,254),(256,232)))

def tx(p, s):
    # scale the flame about its centre (256,251) toward the icon centre (256,256)
    return ((256 + (p[0]-256)*SCALE) * s, (256 + (p[1]-251)*SCALE) * s)

def draw_art(size):
    W = size * SS
    s = W / 512.0
    img = Image.new("RGBA", (W, W), BG + (255,))                # flat blue background

    # the warm light the flame throws
    grad = Image.radial_gradient("L").resize((W, W))            # 0 center -> 255 edge
    gmask = grad.point(lambda v: int(((255 - v) / 255) ** 1.7 * 150))
    glow = Image.new("RGBA", (W, W), GLOW + (0,)); glow.putalpha(gmask)
    glow = glow.filter(ImageFilter.GaussianBlur(int(8 * s)))
    img = Image.alpha_composite(img, glow)

    d = ImageDraw.Draw(img)
    d.polygon([tx(p, s) for p in flame512], fill=FLAME + (255,))
    d.polygon([tx(p, s) for p in core512],  fill=CORE + (230,))
    return img.resize((size, size), Image.LANCZOS)

def save_any(size, name):
    draw_art(size).save(os.path.join(OUT, name)); print("wrote", name)

def save_maskable(size, name, content=0.78):
    canvas = Image.new("RGBA", (size, size), BG + (255,))
    inner = int(size * content)
    canvas.alpha_composite(draw_art(inner), ((size - inner) // 2, (size - inner) // 2))
    canvas.save(os.path.join(OUT, name)); print("wrote", name)

def save_apple(size, name):
    draw_art(size).convert("RGB").save(os.path.join(OUT, name)); print("wrote", name)

if __name__ == "__main__":
    save_any(192, "icon-192.png")
    save_any(512, "icon-512.png")
    save_maskable(512, "icon-maskable-512.png")
    save_apple(180, "apple-touch-icon.png")
