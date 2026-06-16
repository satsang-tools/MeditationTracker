"""Regenerate the PWA PNG icons from the candle-flame motif (matches icon.svg).

Requires Pillow:  pip install Pillow
Run from this folder:  python make_icons.py
"""
import os
from PIL import Image, ImageDraw

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons")
os.makedirs(OUT, exist_ok=True)
SS = 4  # supersample for clean edges

BG    = (0x15, 0x12, 0x0D)
FLAME = (0xE6, 0xA2, 0x4C)
CORE  = (0xFD, 0xE8, 0xC6)

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
    img = Image.new("RGBA", (W, W), BG + (255,))
    grad = Image.radial_gradient("L").resize((W, W))            # 0 center -> 255 edge
    alpha = grad.point(lambda v: int(((255 - v) / 255) ** 1.6 * 150))
    glow = Image.new("RGBA", (W, W), FLAME + (0,)); glow.putalpha(alpha)
    img = Image.alpha_composite(img, glow)

    d = ImageDraw.Draw(img)
    s = W / 512.0
    cx = cy = W / 2; r = 150 * s
    d.ellipse([cx - r, cy - r, cx + r, cy + r], outline=FLAME + (95,), width=max(1, int(4 * s)))
    d.polygon([(x * s, y * s) for x, y in flame512], fill=FLAME + (255,))
    d.polygon([(x * s, y * s) for x, y in core512],  fill=CORE + (217,))
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
