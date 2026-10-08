"""Open GUI Blender with this checkout's addon on the Blend Data example.

    python scripts/open_example.py [out.blend]

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
    output = os.path.abspath(
        sys.argv[1]
        if len(sys.argv) > 1
        else os.path.join(tempfile.gettempdir(), "blend_data_example.blend")
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
            [find_blender(), "--python", SCRIPT, "--", output],
            env=env,
            stdout=out,
            stderr=subprocess.STDOUT,
            start_new_session=True,
        )
    print(f"Blender is opening {output}")
    print(f"Log: {log}")


if __name__ == "__main__":
    main()
