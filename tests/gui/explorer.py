"""The data explorer's operators in a real node editor: browsing leaves nodes
alone, Use This Path / Go to Its Path, + adds a node.

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


def check(condition, reason):
    if not condition:
        raise AssertionError(reason)


def editor(tree):
    """Override for a node editor showing `tree` with its sidebar open."""
    window = bpy.context.window_manager.windows[0]
    area = max(window.screen.areas, key=lambda a: a.width * a.height)
    area.type = "NODE_EDITOR"
    space = area.spaces.active
    space.tree_type = "ScriptingNodeTree"
    space.node_tree = tree
    space.show_region_ui = True
    region = next(r for r in area.regions if r.type == "WINDOW")
    return bpy.context.temp_override(
        window=window, area=area, region=region, space_data=space
    )


def step():
    try:
        s = state["step"]
        state["step"] += 1
        if s == 0:
            helpers.enable_addon()
            cube = bpy.data.objects["Cube"]
            cube.modifiers.new("Bevel", "BEVEL")
            bpy.context.view_layer.objects.active = cube
            tree = helpers.new_tree("Explorer")
            node = helpers.add_node(tree, "SNA_Node_BlendData")
            node.path = "active_object"
            tree.nodes.active = node
            helpers.flush()
            ui = bpy.context.scene.sna.ui
            ui.explorer_path = ""
            with editor(tree):
                # browsing never changes the selected node
                bpy.ops.sna.explorer_open(root="CONTEXT")
                bpy.ops.sna.explorer_open(member="active_object")
                bpy.ops.sna.explorer_open(member="modifiers")
                bpy.ops.sna.explorer_open(item_mode="NAME", item_name="Bevel")
                path = "bpy.context.active_object.modifiers['Bevel']"
                check(ui.explorer_path == path, ui.explorer_path)
                check(node.path == "active_object", f"node changed: {node.path}")
                # ... until Use This Path
                check(bpy.ops.sna.explorer_use_for_node() == {"FINISHED"}, "use")
                check(node.path == "active_object.modifiers[]", node.path)
                check(node.socket("key_0").value == "Bevel", "key value")
                # back, home, go to the node's path
                bpy.ops.sna.explorer_back(count=2)
                check(
                    ui.explorer_path == "bpy.context.active_object.modifiers",
                    ui.explorer_path,
                )
                bpy.ops.sna.explorer_back(count=-1)
                check(ui.explorer_path == "", "home")
                check(bpy.ops.sna.explorer_go_to_node() == {"FINISHED"}, "go to")
                check(ui.explorer_path == path, f"go to: {ui.explorer_path}")
                # + adds a node with the whole path
                bpy.ops.sna.explorer_add(member="width")
                added = tree.nodes.active
                check(added != node, "no node added")
                check(added.path_root == "CONTEXT", added.path_root)
                check(added.path == "active_object.modifiers[].width", added.path)
                check(added.socket("key_0").value == "Bevel", "added key")
        elif s == 1:
            helpers.flush()
            tree = bpy.data.node_groups["Explorer"]
            check(helpers.sn("src.core.errors").addon_error is None, "addon error")
            source = helpers.tree_source(tree)
            check("Explorer" in tree.name and source, "no source")
            print("GUI TEST PASSED")
            bpy.ops.wm.quit_blender()
            return None
    except Exception:
        traceback.print_exc()
        print("GUI TEST FAILED: " + traceback.format_exc().strip().splitlines()[-1])
        bpy.ops.wm.quit_blender()
        return None
    return 0.3


bpy.app.timers.register(step, first_interval=1.0)
