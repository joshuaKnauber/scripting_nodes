"""Regenerate the screenshots used in the docs.

    python scripts/docs_screenshots.py            # all of them
    python scripts/docs_screenshots.py first-addon  # only matching names

Every `website/screenshots/<name>.py` scenario (files starting with `_` are
shared helpers) (same format as tests/visual/scenarios) is captured, framed on
the wallpaper (scripts/screenshot_frame.py) and saved as
`website/public/screenshots/<name>.webp`, which docs pages reference as
`![...](/screenshots/<name>.webp)`.

Settings a scenario can have, besides the driver's (AREA_ONLY, ZOOM_OUT,
UI_SCALE, LAYOUT, SIDEBAR_TAB):
    WINDOW_SIZE = (w, h)        Blender window size, default (1600, 1000)
    CROP = (x0, y0, x1, y1)     keep only this part of the capture, fractions
    FRAME = "float"             placement on the wallpaper (see screenshot_frame)
"""

import ast
import glob
import os
import sys
import tempfile

from PIL import Image

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from screenshot import take  # noqa: E402
from screenshot_frame import frame  # noqa: E402
from test import REPO_ROOT  # noqa: E402

DEFAULTS = {"WINDOW_SIZE": (1600, 1000), "CROP": None, "FRAME": "float"}


def settings(path):
    """Module-level settings, read without importing the scenario (needs bpy)."""
    found = dict(DEFAULTS)
    with open(path) as f:
        for node in ast.parse(f.read()).body:
            if isinstance(node, ast.Assign):
                for target in node.targets:
                    if getattr(target, "id", None) in DEFAULTS:
                        found[target.id] = ast.literal_eval(node.value)
    return found


def crop(path, box):
    image = Image.open(path)
    x0, y0, x1, y1 = box
    w, h = image.size
    image.crop((round(x0 * w), round(y0 * h), round(x1 * w), round(y1 * h))).save(path)


SCENARIOS = os.path.join(REPO_ROOT, "website", "screenshots")
OUTPUT = os.path.join(REPO_ROOT, "website", "public", "screenshots")


def main():
    filters = sys.argv[1:]
    scenarios = sorted(
        path
        for path in glob.glob(os.path.join(SCENARIOS, "*.py"))
        if not os.path.basename(path).startswith("_")  # shared helpers
    )
    if filters:
        scenarios = [
            s for s in scenarios if any(f in os.path.basename(s) for f in filters)
        ]
    if not scenarios:
        sys.exit("No matching scenarios in website/screenshots/")

    failed = []
    raw_dir = tempfile.mkdtemp(prefix="sn_screenshots_")
    for scenario in scenarios:
        name = os.path.splitext(os.path.basename(scenario))[0]
        options = settings(scenario)
        raw = os.path.join(raw_dir, name + ".png")
        output = os.path.join(OUTPUT, name + ".webp")
        print(f"{name} ...", end=" ", flush=True)
        error = take(scenario, raw, options["WINDOW_SIZE"])
        if error:
            print("FAILED")
            print(error)
            failed.append(name)
            continue
        if options["CROP"]:
            crop(raw, options["CROP"])
        frame(raw, output, options["FRAME"])
        print(os.path.relpath(output, REPO_ROOT))
    if failed:
        sys.exit(f"{len(failed)} failed: {', '.join(failed)}")


if __name__ == "__main__":
    main()
