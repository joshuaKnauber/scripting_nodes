"""Open GUI Blender on a scenario and save a screenshot.

    python scripts/screenshot.py tests/visual/scenarios/basic.py out.png

Uses a throwaway user profile (like scripts/test.py), so your own Blender
setup is never touched.
"""

import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test import REPO_ROOT, find_blender, make_user_resources  # noqa: E402

NO_SPLASH = (
    "import bpy; bpy.context.preferences.view.show_splash = False; "
    "bpy.ops.wm.save_userpref()"
)
DRIVER = os.path.join(REPO_ROOT, "tests", "visual", "driver.py")


def take(scenario, output, size=(1600, 1000)):
    """Screenshot `scenario` into `output`. Returns Blender's output on failure."""
    scenario = os.path.abspath(scenario)
    output = os.path.abspath(output)
    os.makedirs(os.path.dirname(output), exist_ok=True)
    user_resources = make_user_resources()
    env = dict(os.environ, BLENDER_USER_RESOURCES=user_resources)
    # Save prefs without the splash / quick-setup screen into the temp profile
    subprocess.run(
        [find_blender(), "-b", "--factory-startup", "--python-expr", NO_SPLASH],
        env=env,
        capture_output=True,
    )
    cmd = [
        find_blender(),
        "--window-geometry",
        "0",
        "0",
        str(size[0]),
        str(size[1]),
        "--python",
        DRIVER,
        "--",
        scenario,
        output,
    ]
    try:
        result = subprocess.run(
            cmd, env=env, capture_output=True, text=True, timeout=120
        )
    finally:
        shutil.rmtree(user_resources, ignore_errors=True)
    out = result.stdout + result.stderr
    if "SCREENSHOT FAILED" in out or not os.path.exists(output):
        return out[-4000:]
    return None


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    error = take(sys.argv[1], sys.argv[2])
    if error:
        print(error)
        sys.exit(1)
    print(os.path.abspath(sys.argv[2]))


if __name__ == "__main__":
    main()
