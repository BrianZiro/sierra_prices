"""
generate_icons.py

Generates all PWA icon sizes from a source logo image.

Usage:
    python generate_icons.py

Reads:  prices/static/icons/logo.png
Writes: prices/static/icons/icon-<size>.png  (for each required size)
        prices/static/icons/logo-<size>.png  (optional, if you want multiple logo sizes)
        prices/static/icons/apple-touch-icon.png
        prices/static/icons/favicon-32x32.png
        prices/static/icons/favicon-16x16.png

The source image must be square. If it isn't, it will be padded with the
chosen background color and centered.
"""

import os
import sys
from PIL import Image

# ----- Config -----
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ICONS_DIR = os.path.join(BASE_DIR, 'prices', 'static', 'icons')
SOURCE_LOGO = os.path.join(ICONS_DIR, 'logo.png')

# PWA sizes (must match manifest.json)
ICON_SIZES = [72, 96, 128, 144, 152, 192, 384, 512]

# Extra icons
APPLE_TOUCH_SIZE = 180
FAVICON_32 = 32
FAVICON_16 = 16

# Padding background for non-square logos. Use (0, 0, 0, 0) for transparent.
PADDING_COLOR = (0, 0, 0, 0)


def ensure_dir(path):
    if not os.path.isdir(path):
        os.makedirs(path)


def load_source(path):
    if not os.path.isfile(path):
        print(f"[ERROR] Source logo not found at: {path}")
        sys.exit(1)
    img = Image.open(path).convert('RGBA')
    print(f"[OK] Loaded source logo: {path}  ({img.width}x{img.height})")
    return img


def make_square(img, bg=PADDING_COLOR):
    """If the image is not square, pad it to a square with transparent bg."""
    w, h = img.size
    if w == h:
        return img

    side = max(w, h)
    square = Image.new('RGBA', (side, side), bg)
    # Center the original image
    square.paste(img, ((side - w) // 2, (side - h) // 2), img)
    print(f"[OK] Padded non-square logo {w}x{h} -> {side}x{side}")
    return square


def save_resized(img, size, out_path):
    resized = img.resize((size, size), Image.LANCZOS)
    resized.save(out_path, format='PNG', optimize=True)
    print(f"[OK] Wrote {out_path}  ({size}x{size})")


def main():
    ensure_dir(ICONS_DIR)

    source = load_source(SOURCE_LOGO)
    source = make_square(source)

    # 1) PWA icons: icon-<size>.png
    for size in ICON_SIZES:
        out = os.path.join(ICONS_DIR, f'icon-{size}.png')
        save_resized(source, size, out)

    # 2) Apple touch icon
    out = os.path.join(ICONS_DIR, 'apple-touch-icon.png')
    save_resized(source, APPLE_TOUCH_SIZE, out)

    # 3) Favicons
    save_resized(source, FAVICON_32, os.path.join(ICONS_DIR, 'favicon-32x32.png'))
    save_resized(source, FAVICON_16, os.path.join(ICONS_DIR, 'favicon-16x16.png'))

    # 4) Also save a 512 version as logo.png fallback if it wasn't already square
    #    (optional — comment out if you don't want this)
    # save_resized(source, 512, os.path.join(ICONS_DIR, 'logo-512.png'))

    print("\n[DONE] All icons generated successfully.")
    print(f"[INFO] Output directory: {ICONS_DIR}")


if __name__ == '__main__':
    main()