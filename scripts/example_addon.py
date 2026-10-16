"""Build an example add-on and export it as shipped.

    python scripts/example_addon.py [toolkit | every_node] [out_dir]

Builds `tests/visual/scenarios/_<name>_demo.py` (default: toolkit, the
Object Toolkit; every_node: every node with its defaults) in headless
Blender, prints node errors, writes the export build unzipped into `out_dir`
(default: builds/<name>/) together with the .blend, then runs `ruff check`
and `ruff format --check` on it with the rules of generated code
(tests/snapshots/ruff.toml). Exits non-zero on findings (CI).
tests/test_example_addon.py compares the toolkit's export against its
snapshot. Uses a throwaway user profile like scripts/test.py.
"""

import os
import shutil
import subprocess
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from test import REPO_ROOT, find_blender, make_user_resources  # noqa: E402

BUILD = """
import os, sys, traceback
import bpy
sys.path.insert(0, {tests!r})
sys.path.insert(0, {scenarios!r})
import helpers
import _{name}_demo as demo

out = {out!r}
try:
    helpers.enable_addon()
    helpers.reset_file()
    demo.build()
    errors = helpers.sn("src.core.errors")
    problems = 0
    for tree in bpy.data.node_groups:
        for node in tree.nodes:
            message = errors.node_message(getattr(node, "id", ""))
            if message:
                problems += 1
                print(f"NODE ERROR {{tree.name}} / {{node.name}}: {{message}}")
    files = helpers.sn("src.core.ops.export").build_files()
    for rel, source in files.items():
        path = os.path.join(out, "addon", rel)
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "w") as f:
            f.write(source)
    bpy.ops.wm.save_as_mainfile(filepath=os.path.join(out, "{name}.blend"))
    print(f"BUILT {{len(files)}} files, {{problems}} node errors")
except Exception:
    traceback.print_exc()
    sys.exit(1)
"""


# every node with its defaults: unconnected inputs give conditions on
# constants (`None == None`, `x in []`) a real add-on wouldn't have
IGNORE = {"every_node": ["--ignore", "RUF060,E711,SIM222,SIM223,RUF034"]}


def main():
    args = sys.argv[1:]
    name = args.pop(0) if args and args[0] in ("toolkit", "every_node") else "toolkit"
    out = os.path.abspath(args[0] if args else os.path.join(REPO_ROOT, "builds", name))
    shutil.rmtree(out, ignore_errors=True)
    os.makedirs(out)
    script = os.path.join(out, "_build.py")
    with open(script, "w") as f:
        f.write(
            BUILD.format(
                tests=os.path.join(REPO_ROOT, "tests"),
                scenarios=os.path.join(REPO_ROOT, "tests", "visual", "scenarios"),
                out=out,
                name=name,
            )
        )
    user_resources = make_user_resources()
    env = dict(os.environ, BLENDER_USER_RESOURCES=user_resources)
    try:
        result = subprocess.run(
            [
                find_blender(),
                "-b",
                "--factory-startup",
                "--python-exit-code",
                "1",
                "--python",
                script,
            ],
            env=env,
            capture_output=True,
            text=True,
        )
    finally:
        shutil.rmtree(user_resources, ignore_errors=True)
        os.remove(script)
    lines = (result.stdout + result.stderr).splitlines()
    shown = [
        line for line in lines if "ERROR" in line or "BUILT" in line or "Error" in line
    ]
    print("\n".join(shown or lines[-40:]))
    if result.returncode:
        print("\n".join(lines[-40:]))
        sys.exit(result.returncode)
    print(f"\nExported to {out}/addon\nruff:", flush=True)
    config = ["--config", os.path.join(REPO_ROOT, "tests", "snapshots", "ruff.toml")]
    addon = os.path.join(out, "addon")
    check = subprocess.run(
        ["uvx", "ruff", "check", "--no-cache", "--statistics", *config]
        + IGNORE.get(name, [])
        + [addon]
    )
    form = subprocess.run(["uvx", "ruff", "format", "--check", *config, addon])
    sys.exit(check.returncode or form.returncode)


if __name__ == "__main__":
    main()
