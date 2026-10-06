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
    sys.exit(result.returncode)


if __name__ == "__main__":
    main()
