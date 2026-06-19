"""Regenerate the PWA PNG icons from the glowing-ring motif (matches icon.svg).

Requires Pillow:  pip install Pillow
Run from this folder:  python make_icons.py
"""
import os
from PIL import Image, ImageDraw, ImageFilter

OUT = os.path.join(os.path.dirname(os.path.abspath(__file__)), "icons")
os.makedirs(OUT, exist_ok=True)
SS = 4  # supersample for clean edges

BG   = (0x0B, 0x0D, 0x11)   # cool near-black room
BLUE = (0x2E, 0x86, 0xFF)   # the electric current (glow)
EDGE = (0x5A, 0xA8, 0xFF)   # the crisp ring edge

def draw_art(size):
    W = size * SS
    s = W / 512.0
    img = Image.new("RGBA", (W, W), BG + (255,))

    # the cool light it throws: a soft radial glow from the centre
    grad = Image.radial_gradient("L").resize((W, W))            # 0 center -> 255 edge
    alpha = grad.point(lambda v: int(((255 - v) / 255) ** 1.6 * 130))
    glow = Image.new("RGBA", (W, W), BLUE + (0,)); glow.putalpha(alpha)
    img = Image.alpha_composite(img, glow)

    cx = cy = W / 2.0; r = 150 * s
    bbox = [cx - r, cy - r, cx + r, cy + r]

    # the breathing ring: a blurred blue halo ...
    halo = Image.new("RGBA", (W, W), (0, 0, 0, 0))
    ImageDraw.Draw(halo).ellipse(bbox, outline=BLUE + (255,), width=max(1, int(11 * s)))
    halo = halo.filter(ImageFilter.GaussianBlur(radius=int(16 * s)))
    img = Image.alpha_composite(img, halo)

    # ... and the crisp electric edge on top
    ImageDraw.Draw(img).ellipse(bbox, outline=EDGE + (255,), width=max(1, int(5 * s)))
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
