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

BG_CENTER = (0x3A, 0x93, 0xFF)   # blue at the centre
BG_EDGE   = (0x14, 0x64, 0xDC)   # deeper blue at the edges
FLAME     = (0xFF, 0x8A, 0x2E)   # the orange flame
CORE      = (0xFF, 0xE9, 0xC8)   # warm core
GLOW      = (0xFF, 0x8A, 0x2E)   # the light it throws

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

def draw_art(size):
    W = size * SS
    s = W / 512.0
    grad = Image.radial_gradient("L").resize((W, W))            # 0 center -> 255 edge

    # blue radial background: BG_CENTER in the middle, BG_EDGE at the rim
    bg = Image.new("RGBA", (W, W), BG_EDGE + (255,))
    center = Image.new("RGBA", (W, W), BG_CENTER + (255,))
    bg = Image.composite(center, bg, grad.point(lambda v: 255 - v))

    # the warm light the flame throws
    gmask = grad.point(lambda v: int(((255 - v) / 255) ** 1.7 * 150))
    glow = Image.new("RGBA", (W, W), GLOW + (0,)); glow.putalpha(gmask)
    glow = glow.filter(ImageFilter.GaussianBlur(int(8 * s)))
    img = Image.alpha_composite(bg, glow)

    d = ImageDraw.Draw(img)
    d.polygon([(x * s, y * s) for x, y in flame512], fill=FLAME + (255,))
    d.polygon([(x * s, y * s) for x, y in core512],  fill=CORE + (230,))
    return img.resize((size, size), Image.LANCZOS)

def save_any(size, name):
    draw_art(size).save(os.path.join(OUT, name)); print("wrote", name)

def save_maskable(size, name, content=0.78):
    canvas = Image.new("RGBA", (size, size), BG_EDGE + (255,))
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
