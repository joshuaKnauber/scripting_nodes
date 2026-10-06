"""Runs inside GUI Blender (see scripts/screenshot.py).

Enables the addon, runs `setup()` from the scenario module, turns the biggest
area into a node editor showing the returned tree, waits for a few redraws,
saves a screenshot and quits.

A scenario may also define `after(context)` which runs once the addon has
flushed (e.g. to open panels or trigger generated operators), and set
`AREA_ONLY = True` to capture just the node editor instead of the window and
`ZOOM_OUT = n` to zoom out n steps after framing the nodes.
"""

import importlib.util
import os
import sys
import traceback

import bpy

sys.stdout.reconfigure(line_buffering=True)
TESTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TESTS_DIR)

import helpers  # noqa: E402

argv = sys.argv[sys.argv.index("--") + 1 :]
SCENARIO, OUTPUT = argv[0], argv[1]

_state = {"step": 0, "scenario": None, "tree": None}


def load_scenario():
    spec = importlib.util.spec_from_file_location("scenario", SCENARIO)
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def main_area():
    window = bpy.context.window_manager.windows[0]
    area = max(window.screen.areas, key=lambda a: a.width * a.height)
    return window, area


def show_tree(tree):
    window, area = main_area()
    area.type = "NODE_EDITOR"
    space = area.spaces.active
    space.tree_type = "ScriptingNodeTree"
    space.node_tree = tree
    space.show_region_ui = True


def frame_all(zoom_out=0):
    window, area = main_area()
    region = next(r for r in area.regions if r.type == "WINDOW")
    with bpy.context.temp_override(window=window, area=area, region=region):
        bpy.ops.node.view_all()
        for _ in range(zoom_out):
            bpy.ops.view2d.zoom_out()


def step():
    try:
        s = _state["step"]
        _state["step"] += 1
        if s == 0:
            helpers.enable_addon()
            _state["scenario"] = load_scenario()
            _state["tree"] = _state["scenario"].setup()
            helpers.flush()
        elif s == 1:
            if _state["tree"] is not None:
                show_tree(_state["tree"])
            after = getattr(_state["scenario"], "after", None)
            if after:
                after(bpy.context)
            helpers.flush()
        elif s in (3, 4):
            # Twice: the first pass can run before nodes have drawn dimensions
            if _state["tree"] is not None:
                frame_all(getattr(_state["scenario"], "ZOOM_OUT", 0))
        elif s == 5:
            window, area = main_area()
            if getattr(_state["scenario"], "AREA_ONLY", False):
                with bpy.context.temp_override(window=window, area=area):
                    bpy.ops.screen.screenshot_area(filepath=OUTPUT)
            else:
                with bpy.context.temp_override(window=window):
                    bpy.ops.screen.screenshot(filepath=OUTPUT)
            print(f"SCREENSHOT {OUTPUT}")
        elif s == 6:
            bpy.ops.wm.quit_blender()
            return None
        return 0.4
    except Exception:
        traceback.print_exc()
        print("SCREENSHOT FAILED")
        bpy.ops.wm.quit_blender()
        return None


bpy.app.timers.register(step, first_interval=1.0)
