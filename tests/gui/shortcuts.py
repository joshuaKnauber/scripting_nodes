"""Shortcut nodes add keymap items to Blender's add-on keyconfig (None in
background mode) and remove them when the add-on is rebuilt, the node is
deleted or the generated add-on is disabled.

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


def check(condition, reason):
    if not condition:
        raise AssertionError(reason)


def items(idname):
    """Our keymap items running `idname`, as (keymap name, item)."""
    keyconfig = bpy.context.window_manager.keyconfigs.addon
    return [
        (keymap.name, item)
        for keymap in keyconfig.keymaps
        for item in keymap.keymap_items
        if item.idname == idname
    ]


def step():
    try:
        helpers.enable_addon()
        bpy.context.scene.sna.addon.addon_name = "Shortcut Test"
        tree = helpers.new_tree("Shortcuts")
        operator = helpers.add_node(tree, "SNA_Node_Operator")
        operator.socket("label").value = "Greet"
        shortcut = helpers.add_node(tree, "SNA_Node_Shortcut")
        helpers.point(shortcut, "operator_sn", operator)
        shortcut.key = "G"
        shortcut.ctrl = True
        shortcut.keymap = "3D View"
        cube = helpers.add_node(tree, "SNA_Node_Shortcut")
        cube.mode = "BLENDER"
        cube.operator_blender = "mesh.primitive_cube_add"
        cube.keymap = "Object Mode"
        helpers.flush()
        cube.socket("arg_size").value = 4.0
        helpers.flush()
        check(helpers.sn("src.core.errors").addon_error is None, "addon error")

        found = items("shortcut_test.greet")
        check(len(found) == 1, f"greet items: {found}")
        name, item = found[0]
        check(name == "3D View", name)
        check((item.type, item.ctrl, item.shift) == ("G", True, False), "keys")
        found = items("mesh.primitive_cube_add")
        check(len(found) == 1 and found[0][0] == "Object Mode", f"cube: {found}")
        check(found[0][1].properties.size == 4.0, "properties")

        # rebuilding replaces the items instead of adding more
        shortcut.key = "H"
        helpers.flush()
        found = items("shortcut_test.greet")
        check([i.type for _, i in found] == ["H"], f"after rebuild: {found}")

        tree.nodes.remove(shortcut)
        helpers.flush()
        check(items("shortcut_test.greet") == [], "not removed with the node")
        import addon_utils

        addon_utils.disable(bpy.context.scene.sna.addon.module_name)
        check(items("mesh.primitive_cube_add") == [], "not removed on disable")
        print("GUI TEST PASSED")
    except Exception:
        traceback.print_exc()
        print("GUI TEST FAILED: " + traceback.format_exc().strip().splitlines()[-1])
    bpy.ops.wm.quit_blender()
    return None


bpy.app.timers.register(step, first_interval=1.0)
