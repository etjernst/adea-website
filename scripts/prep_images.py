"""Copy the few page images from scrape/images into assets/images with friendly
names, resized and re-compressed for web. Member headshots are handled separately
in Phase 2. Run once (idempotent)."""
import os
from PIL import Image, ImageOps

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, "scrape", "images")
DST = os.path.join(ROOT, "assets", "images")
os.makedirs(DST, exist_ok=True)

# source file -> (friendly name, max long edge px). Logo kept as PNG (transparency).
MAP = {
    "home_00_de444031.png": ("adea-logo.png", 256),
    "home_01_6da15851.jpeg": ("home-hero.jpg", 1500),       # outrigger canoe on river
    "news_01_2fb6ab0c.jpeg": ("region-map.jpg", 1500),      # Australasia map with member pins
    "about_01_0ecfd30e.jpeg": ("road-transport.jpg", 1600), # loaded rural transport
    "home_02_3e7b2c4d.jpeg": ("village-aerial.jpg", 1600),  # aerial view of a village
}


def process(src_name, dst_name, max_edge):
    src = os.path.join(SRC, src_name)
    dst = os.path.join(DST, dst_name)
    im = Image.open(src)
    im = ImageOps.exif_transpose(im)
    w, h = im.size
    scale = min(1.0, max_edge / max(w, h))
    if scale < 1.0:
        im = im.resize((round(w * scale), round(h * scale)), Image.LANCZOS)
    if dst_name.lower().endswith(".png"):
        im.save(dst, "PNG", optimize=True)
    else:
        im.convert("RGB").save(dst, "JPEG", quality=82, optimize=True, progressive=True)
    return os.path.getsize(dst)


if __name__ == "__main__":
    for s, (d, edge) in MAP.items():
        size = process(s, d, edge)
        print(f"{d:24s} {size/1024:6.1f} KB")
    print(f"\nWrote {len(MAP)} images to {DST}")
