"""Put a raw Blender screenshot on the docs wallpaper (website/wallpaper.jpg).

    python scripts/screenshot_frame.py raw.png out.webp [float|corner|right|bottom]

The capture gets rounded corners, a hairline border and a soft shadow, and
sits on a crop of the wallpaper. Every name gets its own crop (seeded by the
output file name), so neighbouring shots on a page don't look identical.

Placements:
    float   padding on all sides (small captures: a few nodes, a panel)
    corner  padding top/left, runs off the right and bottom (full windows)
    right   padding top/left/bottom, runs off the right
    bottom  padding top/left/right, runs off the bottom

Needs Pillow (`pip install pillow`).
"""

import hashlib
import os
import sys

from PIL import Image, ImageChops, ImageDraw, ImageFilter

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
WALLPAPER = os.path.join(REPO_ROOT, "website", "wallpaper.jpg")

MAX_WIDTH = 2400  # 2x of the ~1200px the docs show at most
PADDING = 0.075  # of the capture's longer side
RADIUS = 0.012  # corner radius, of the capture's longer side
PLACEMENTS = ("float", "corner", "right", "bottom")

_wallpaper = None


def wallpaper():
    global _wallpaper
    if _wallpaper is None:
        image = Image.open(WALLPAPER).convert("RGB")
        image.draft("RGB", (3000, 3000))  # the jpg is 6016px, plenty halved
        _wallpaper = image
    return _wallpaper


def background(size, seed):
    """A crop of the wallpaper covering `size`, picked by `seed`."""
    wall = wallpaper()
    digest = hashlib.sha1(seed.encode()).digest()
    # zoom in between 1x and 1.6x so crops differ in scale as well as place
    zoom = 1 + digest[0] / 255 * 0.6
    scale = max(size[0] / wall.width, size[1] / wall.height) * zoom
    w, h = round(size[0] / scale), round(size[1] / scale)
    x = round((wall.width - w) * digest[1] / 255)
    y = round((wall.height - h) * digest[2] / 255)
    return wall.crop((x, y, x + w, y + h)).resize(size, Image.LANCZOS)


def rounded_mask(size, radius):
    # drawn 4x and scaled down: ImageDraw's arcs aren't anti-aliased
    big = Image.new("L", (size[0] * 4, size[1] * 4), 0)
    ImageDraw.Draw(big).rounded_rectangle(
        (0, 0, big.width - 1, big.height - 1), radius * 4, fill=255
    )
    return big.resize(size, Image.LANCZOS)


def frame(raw, output, placement="float"):
    if placement not in PLACEMENTS:
        raise ValueError(f"placement must be one of {PLACEMENTS}, not {placement!r}")
    shot = Image.open(raw).convert("RGB")
    side = max(shot.size)
    pad = round(side * PADDING)
    radius = max(round(side * RADIUS), 6)
    bleed = 2 * radius  # runs just past the edge, hiding the rounded corner

    cut_right = placement in ("corner", "right")
    cut_bottom = placement in ("corner", "bottom")
    width = pad + shot.width + (-bleed if cut_right else pad)
    height = pad + shot.height + (-bleed if cut_bottom else pad)
    canvas = background((width, height), os.path.basename(output))

    # soft shadow, a bit below the window
    mask = rounded_mask(shot.size, radius)
    shadow = Image.new("L", (width, height), 0)
    shadow.paste(mask, (pad, pad + round(side * 0.012)))
    shadow = shadow.filter(ImageFilter.GaussianBlur(side * 0.02))
    canvas.paste(
        Image.new("RGB", canvas.size, (8, 4, 24)),
        mask=shadow.point(lambda v: v * 0.55),
    )

    canvas.paste(shot, (pad, pad), mask)

    # hairline border, light like the edge of a macOS window
    line = max(round(side / 1500), 1)
    inner = rounded_mask(
        (shot.width - 2 * line, shot.height - 2 * line), max(radius - line, 1)
    )
    ring = mask.copy()
    ring.paste(0, (line, line), inner)
    ring = ImageChops.multiply(ring, mask).point(lambda v: v * 0.22)
    canvas.paste(
        Image.new("RGB", canvas.size, (255, 255, 255)),
        (0, 0),
        _at(ring, (pad, pad), canvas.size),
    )

    if canvas.width > MAX_WIDTH:
        canvas = canvas.resize(
            (MAX_WIDTH, round(canvas.height * MAX_WIDTH / canvas.width)), Image.LANCZOS
        )
    os.makedirs(os.path.dirname(os.path.abspath(output)), exist_ok=True)
    if output.endswith(".webp"):
        canvas.save(output, quality=90, method=6)
    else:
        canvas.save(output, optimize=True)


def _at(mask, offset, size):
    """`mask` placed at `offset` on an empty mask of `size`."""
    full = Image.new("L", size, 0)
    full.paste(mask, offset)
    return full


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    frame(sys.argv[1], sys.argv[2], *sys.argv[3:4])
    print(os.path.abspath(sys.argv[2]))


if __name__ == "__main__":
    main()
