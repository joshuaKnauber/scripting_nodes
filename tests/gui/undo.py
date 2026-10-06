"""Real undo/redo in a GUI session: the generated addon follows the undo stack.

Runs inside GUI Blender via `python scripts/test.py --gui`. Prints
"GUI TEST PASSED" or "GUI TEST FAILED: <reason>" and quits.
"""

import os
import sys
import traceback

import bpy

sys.stdout.reconfigure(line_buffering=True)
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
import helpers  # noqa: E402

state = {"step": 0}


def window_override():
    window = bpy.context.window_manager.windows[0]
    return bpy.context.temp_override(window=window, screen=window.screen)


def generated_source():
    tree = bpy.data.node_groups["Undo"]
    runtime = helpers.sn("src.core.runtime")
    path = os.path.join(
        runtime.folder(bpy.context.scene.sna.addon.module_name),
        "addon",
        tree.module_name + ".py",
    )
    with open(path) as f:
        return f.read()


def print_node():
    return next(
        n for n in bpy.data.node_groups["Undo"].nodes if n.bl_idname == "SNA_Node_Print"
    )


def check(condition, reason):
    if not condition:
        raise AssertionError(reason)


def step():
    try:
        s = state["step"]
        state["step"] += 1
        if s == 0:
            helpers.enable_addon()
            bpy.context.scene.sna.addon.addon_name = "Undo Test"
            tree = helpers.new_tree("Undo")
            trigger = helpers.add_node(tree, "SNA_Node_Trigger")
            p = helpers.add_node(tree, "SNA_Node_Print")
            p.inputs[1].value = "before"
            helpers.link(tree, trigger.outputs[0], p.inputs[0])
            helpers.flush()
            with window_override():
                bpy.ops.ed.undo_push(message="before")
        elif s == 1:
            print_node().inputs[1].value = "after"
            helpers.flush()
            check(repr("after") in generated_source(), "edit not applied")
            with window_override():
                bpy.ops.ed.undo_push(message="after")
        elif s == 2:
            with window_override():
                bpy.ops.ed.undo()
        elif s == 3:
            helpers.flush()  # the timer would do this a moment later
            check(print_node().inputs[1].value == "before", "undo didn't restore value")
            check(repr("before") in generated_source(), "addon not rebuilt after undo")
            with window_override():
                bpy.ops.ed.redo()
        elif s == 4:
            helpers.flush()
            check(repr("after") in generated_source(), "addon not rebuilt after redo")
            print("GUI TEST PASSED")
            bpy.ops.wm.quit_blender()
            return None
        return 0.3
    except Exception:
        traceback.print_exc()
        print("GUI TEST FAILED")
        bpy.ops.wm.quit_blender()
        return None


bpy.app.timers.register(step, first_interval=1.0)
