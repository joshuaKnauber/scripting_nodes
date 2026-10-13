"""Open GUI Blender with this checkout's addon on an example.

    python scripts/open_example.py [example.py] [out.blend]

`example.py` builds the file (default: tests/visual/open_blend_data_example.py).

Uses a separate user profile (kept in a temp folder, path printed), so your
own Blender setup and installed Scripting Nodes are never touched. Blender
stays open; the example is saved to `out.blend` (default: a temp file).
"""

import os
import subprocess
import sys
import tempfile

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from screenshot import NO_SPLASH  # noqa: E402
from test import REPO_ROOT, find_blender, make_user_resources  # noqa: E402

SCRIPT = os.path.join(REPO_ROOT, "tests", "visual", "open_blend_data_example.py")


def main():
    args = sys.argv[1:]
    script = (
        os.path.abspath(args.pop(0)) if args and args[0].endswith(".py") else SCRIPT
    )
    name = os.path.splitext(os.path.basename(script))[0].removeprefix("open_")
    output = os.path.abspath(
        args[0] if args else os.path.join(tempfile.gettempdir(), f"{name}.blend")
    )
    user_resources = make_user_resources()
    env = dict(os.environ, BLENDER_USER_RESOURCES=user_resources)
    subprocess.run(
        [find_blender(), "-b", "--factory-startup", "--python-expr", NO_SPLASH],
        env=env,
        capture_output=True,
    )
    log = os.path.join(user_resources, "blender.log")
    with open(log, "w") as out:
        subprocess.Popen(
            [find_blender(), "--python", script, "--", output],
            env=env,
            stdout=out,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
    print(f"Blender is opening {output}")
    print(f"Log: {log}")


if __name__ == "__main__":
    main()
