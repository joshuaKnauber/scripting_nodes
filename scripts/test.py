"""Run the headless Blender test suite.

    python scripts/test.py                 # all tests
    python scripts/test.py -k compile      # only tests whose id contains "compile"

Blender is taken from $BLENDER, else from config.yaml (BLENDER_EXECUTABLE).
Every run uses a throwaway BLENDER_USER_RESOURCES directory so it never touches
your real preferences, extensions or generated addons. The addon source folder
is symlinked into the temp `user_default` extension repo, so no build step is
needed.
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ADDON_SRC = os.path.join(REPO_ROOT, "addon", "scripting_nodes")
RUNNER = os.path.join(REPO_ROOT, "tests", "runner.py")


def find_blender():
    if os.environ.get("BLENDER"):
        return os.environ["BLENDER"]
    config_path = os.path.join(REPO_ROOT, "config.yaml")
    if os.path.exists(config_path):
        with open(config_path) as f:
            for line in f:
                if line.strip().startswith("BLENDER_EXECUTABLE"):
                    return line.split(":", 1)[1].strip().strip("'\"")
    sys.exit("Blender not found: set $BLENDER or BLENDER_EXECUTABLE in config.yaml")


def make_user_resources(keep=None):
    root = keep or tempfile.mkdtemp(prefix="sn_test_")
    repo = os.path.join(root, "extensions", "user_default")
    os.makedirs(repo, exist_ok=True)
    link = os.path.join(repo, "scripting_nodes")
    if os.path.lexists(link):
        os.remove(link) if os.path.islink(link) else shutil.rmtree(link)
    try:
        os.symlink(ADDON_SRC, link, target_is_directory=True)
    except OSError:
        # Windows without symlink rights - fall back to a copy
        shutil.copytree(ADDON_SRC, link, ignore=shutil.ignore_patterns("__pycache__"))
    return root


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("-k", dest="pattern", default="", help="substring filter")
    parser.add_argument("--keep", action="store_true", help="keep temp dir")
    parser.add_argument("-v", "--verbose", action="store_true")
    parser.add_argument(
        "--gui", action="store_true", help="also run tests/gui/*.py in GUI Blender"
    )
    args = parser.parse_args()

    blender = find_blender()
    user_resources = make_user_resources()
    env = dict(os.environ, BLENDER_USER_RESOURCES=user_resources, PYTHONUNBUFFERED="1")
    cmd = [
        blender,
        "-b",
        "--factory-startup",
        "--python-exit-code",
        "1",
        "--python",
        RUNNER,
        "--",
        "--pattern",
        args.pattern,
    ]
    if args.verbose:
        cmd.append("--verbose")
    try:
        result = subprocess.run(cmd, env=env)
    finally:
        if args.keep:
            print(f"Kept user resources at {user_resources}")
        else:
            shutil.rmtree(user_resources, ignore_errors=True)
    failed = result.returncode != 0
    if args.gui:
        failed |= not run_gui_tests(blender, args.pattern)
    sys.exit(1 if failed else 0)


def run_gui_tests(blender, pattern=""):
    """Each tests/gui/*.py drives a real Blender window and prints
    "GUI TEST PASSED" / "GUI TEST FAILED"."""
    gui_dir = os.path.join(REPO_ROOT, "tests", "gui")
    ok = True
    for name in sorted(os.listdir(gui_dir)):
        if not name.endswith(".py") or pattern not in name:
            continue
        user_resources = make_user_resources()
        env = dict(os.environ, BLENDER_USER_RESOURCES=user_resources)
        subprocess.run(
            [blender, "-b", "--factory-startup", "--python-expr", NO_SPLASH],
            env=env,
            capture_output=True,
        )
        try:
            result = subprocess.run(
                [blender, "--python", os.path.join(gui_dir, name)],
                env=env,
                capture_output=True,
                text=True,
                timeout=180,
            )
            output = result.stdout + result.stderr
        except subprocess.TimeoutExpired as e:
            output = f"timeout\n{e.stdout or ''}"
        finally:
            shutil.rmtree(user_resources, ignore_errors=True)
        passed = "GUI TEST PASSED" in output
        print(f"gui/{name}: {'ok' if passed else 'FAILED'}")
        if not passed:
            print(output[-3000:])
            ok = False
    return ok


NO_SPLASH = (
    "import bpy; bpy.context.preferences.view.show_splash = False; "
    "bpy.ops.wm.save_userpref()"
)


if __name__ == "__main__":
    main()
