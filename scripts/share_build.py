"""Package a zip to share (testers, beta) from the last commit.

    python scripts/share_build.py           # scripting_nodes-<version>.zip
    python scripts/share_build.py --beta    # scripting_nodes-<version>-beta.zip
    python scripts/share_build.py --output dist   # only there (CI releases)

Exports HEAD (uncommitted changes aren't included) to a temp folder, leaves
out features that aren't ready to share (LEFT_OUT), builds the extension with
the copy's scripts/build.py and copies the zip to builds/ and the Desktop.
The checkout itself isn't touched. Packaging only: no tests, no validation.
"""

import argparse
import os
import shutil
import subprocess
import sys
import tempfile

REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = "addon/scripting_nodes/src"

# Features in main that builds leave out until they're ready. Remove an entry
# (and its cleanup below) when the feature ships.
LEFT_OUT = {}


def manifest_version(copy):
    with open(
        os.path.join(copy, "addon", "scripting_nodes", "blender_manifest.toml")
    ) as f:
        for line in f:
            if line.startswith("version"):
                return line.split("=")[1].strip().strip('"')
    raise SystemExit("No version in blender_manifest.toml")


def main():
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--beta", action="store_true", help="name it <version>-beta")
    parser.add_argument("--version", help="version to build (default: the manifest's)")
    parser.add_argument(
        "--output", help="folder for the zip (default: builds/ and the Desktop)"
    )
    args = parser.parse_args()

    commit = subprocess.run(
        ["git", "log", "-1", "--format=%h %s"],
        cwd=REPO_ROOT,
        capture_output=True,
        text=True,
    ).stdout.strip()
    dirty = subprocess.run(
        ["git", "status", "--porcelain"], cwd=REPO_ROOT, capture_output=True, text=True
    ).stdout.strip()

    copy = tempfile.mkdtemp(prefix="sn_share_build_")
    archive = subprocess.Popen(
        ["git", "archive", "HEAD"], cwd=REPO_ROOT, stdout=subprocess.PIPE
    )
    subprocess.run(["tar", "-x", "-C", copy], stdin=archive.stdout, check=True)
    archive.wait()
    if os.path.exists(os.path.join(REPO_ROOT, "config.yaml")):
        shutil.copy(os.path.join(REPO_ROOT, "config.yaml"), copy)

    for paths in LEFT_OUT.values():
        for rel in paths:
            path = os.path.join(copy, rel)
            if os.path.isdir(path):
                shutil.rmtree(path)
            elif os.path.exists(path):
                os.remove(path)

    version = args.version or manifest_version(copy)
    if args.beta and "-" not in version:
        version += "-beta"
    result = subprocess.run(
        [sys.executable, "scripts/build.py", "--version", version],
        cwd=copy, capture_output=True, text=True,
    )  # fmt: skip
    zip_name = f"scripting_nodes-{version}.zip"
    built = os.path.join(copy, "builds", zip_name)
    if result.returncode != 0 or not os.path.exists(built):
        print(result.stdout[-3000:], result.stderr[-3000:])
        raise SystemExit("Build failed")

    outputs = [os.path.join(REPO_ROOT, "builds"), os.path.expanduser("~/Desktop")]
    if args.output:
        outputs = [os.path.abspath(args.output)]
    for folder in outputs:
        os.makedirs(folder, exist_ok=True)
        shutil.copy(built, folder)
    shutil.rmtree(copy, ignore_errors=True)

    print(f"Built {zip_name} from {commit}")
    print(f"Left out: {', '.join(LEFT_OUT) or 'nothing'}")
    if dirty:
        print("Note: uncommitted changes aren't in the build")
    for folder in outputs:
        print(os.path.join(folder, zip_name))


if __name__ == "__main__":
    main()
