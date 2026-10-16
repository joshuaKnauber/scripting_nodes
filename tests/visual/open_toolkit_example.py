"""Opens GUI Blender on the Object Toolkit, the example add-on of the code
quality work (tests/visual/scenarios/_toolkit_demo.py). Run by
scripts/open_example.py:

    python scripts/open_example.py tests/visual/open_toolkit_example.py

The node editor shows the Interface tree with the sidebar open (Addon ›
Extensions Platform is checked), the 3D viewport the add-on's panel.
"""

import os
import sys
import traceback

import bpy

TESTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TESTS_DIR)
sys.path.insert(0, os.path.join(TESTS_DIR, "visual", "scenarios"))

import _toolkit_demo  # noqa: E402
import helpers  # noqa: E402

OUTPUT = sys.argv[sys.argv.index("--") + 1]


def show(tree):
    window = bpy.context.window_manager.windows[0]
    area = max(
        (a for a in window.screen.areas if a.type == "VIEW_3D"),
        key=lambda a: a.width * a.height,
    )
    region = next(r for r in area.regions if r.type == "WINDOW")
    with bpy.context.temp_override(window=window, area=area, region=region):
        bpy.ops.screen.area_split(direction="VERTICAL", factor=0.62)
    views = [a for a in window.screen.areas if a.type == "VIEW_3D"]
    left = min(views, key=lambda a: a.x)
    right = max(views, key=lambda a: a.x)
    left.type = "NODE_EDITOR"
    space = left.spaces.active
    space.tree_type = "ScriptingNodeTree"
    space.node_tree = tree
    for area, category in ((left, "Scripting Nodes"), (right, "Toolkit")):
        area.spaces.active.show_region_ui = True
        for region in area.regions:
            if region.type == "UI":
                try:
                    region.active_panel_category = category
                except Exception:
                    pass
    return window, left


def frame(window, area):
    region = next(r for r in area.regions if r.type == "WINDOW")
    with bpy.context.temp_override(window=window, area=area, region=region):
        bpy.ops.node.view_all()


def start():
    try:
        helpers.enable_addon()
        trees = _toolkit_demo.build()
        helpers.sn("src.core.export_check").run()
        window, area = show(trees["Interface"])
        bpy.app.timers.register(lambda: frame(window, area), first_interval=0.5)
        bpy.ops.wm.save_as_mainfile(filepath=OUTPUT)
        print("EXAMPLE READY", OUTPUT, flush=True)
    except Exception:
        traceback.print_exc()
        print("EXAMPLE FAILED", flush=True)


if __name__ == "__main__":  # also imported by open_export_check_example.py
    bpy.app.timers.register(start, first_interval=0.5)
