"""Regenerate the screenshots used in the docs.

    python scripts/docs_screenshots.py            # all of them
    python scripts/docs_screenshots.py first-addon  # only matching names

Every `website/screenshots/<name>.py` scenario (same format as
tests/visual/scenarios) is rendered to `website/public/screenshots/<name>.png`,
which docs pages reference as `![...](/screenshots/<name>.png)`.
A scenario can set `WINDOW_SIZE = (w, h)` to control the shot's size.
"""

import ast
import glob
import os
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from screenshot import take  # noqa: E402
from test import REPO_ROOT  # noqa: E402


def window_size(path):
    """Read a module-level WINDOW_SIZE without importing the scenario (needs bpy)."""
    with open(path) as f:
        for node in ast.parse(f.read()).body:
            if isinstance(node, ast.Assign) and any(
                getattr(t, "id", None) == "WINDOW_SIZE" for t in node.targets
            ):
                return ast.literal_eval(node.value)
    return (1600, 1000)


SCENARIOS = os.path.join(REPO_ROOT, "website", "screenshots")
OUTPUT = os.path.join(REPO_ROOT, "website", "public", "screenshots")


def main():
    filters = sys.argv[1:]
    scenarios = sorted(glob.glob(os.path.join(SCENARIOS, "*.py")))
    if filters:
        scenarios = [
            s for s in scenarios if any(f in os.path.basename(s) for f in filters)
        ]
    if not scenarios:
        sys.exit("No matching scenarios in website/screenshots/")

    failed = []
    for scenario in scenarios:
        name = os.path.splitext(os.path.basename(scenario))[0]
        output = os.path.join(OUTPUT, name + ".png")
        print(f"{name} ...", end=" ", flush=True)
        error = take(scenario, output, window_size(scenario))
        if error:
            print("FAILED")
            print(error)
            failed.append(name)
        else:
            print(os.path.relpath(output, REPO_ROOT))
    if failed:
        sys.exit(f"{len(failed)} failed: {', '.join(failed)}")


if __name__ == "__main__":
    main()
