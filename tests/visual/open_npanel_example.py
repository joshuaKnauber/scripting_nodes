"""Opens GUI Blender with a panel in the 3D viewport's sidebar (N panel), in
a tab of its own: "My Tools" (run by
scripts/open_example.py tests/visual/open_npanel_example.py).

The panel has a label, a button adding a monkey and two Blender settings.
The node editor is on the left, the 3D viewport with its sidebar open on the
right.
"""

import os
import sys
import traceback

import bpy

TESTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TESTS_DIR)

import helpers  # noqa: E402

OUTPUT = sys.argv[sys.argv.index("--") + 1]
CATEGORY = "My Tools"


def blender_operator(idname):
    operator_call = helpers.sn("src.nodes._operator_call")
    return next(
        display
        for display, bl_idname in operator_call.blender_operator_choices()
        if bl_idname == idname
    )


def build():
    bpy.context.scene.sna.addon.addon_name = "My Tools"
    tree = helpers.new_tree("My Tools")
    add = lambda idname, x, y: helpers.add_node(tree, idname, (x, y))  # noqa: E731
    link = lambda a, b: helpers.link(tree, a, b)  # noqa: E731

    panel = add("SNA_Node_Panel", -900, 100)
    panel.socket("label").value = "My Tools"
    panel.panel_space_type = "VIEW_3D"
    panel.panel_region_type = "UI"
    panel.panel_category = CATEGORY
    panel.socket("icon").value = "TOOL_SETTINGS"  # the tab with compact tabs

    label = add("SNA_Node_Label", -600, 150)
    label.socket("text").value = "Made with Scripting Nodes"
    label.socket("icon").value = "NODETREE"

    button = add("SNA_Node_Button", -300, 150)
    button.mode = "BLENDER"
    button.operator_blender = blender_operator("mesh.primitive_monkey_add")
    helpers.flush()
    button.socket("label").value = "Add Monkey"
    button.socket("icon").value = "MESH_MONKEY"

    simplify = add("SNA_Node_Checkbox", 0, 150)
    simplify.mode = "BLENDER"
    simplify.path = "scene.render.use_simplify"

    frame_end = add("SNA_Node_NumberField", 300, 150)
    frame_end.mode = "BLENDER"
    frame_end.path = "scene.frame_end"

    link(panel.outputs["body"], label.inputs[0])
    link(label.outputs[0], button.inputs[0])
    link(button.outputs[0], simplify.inputs[0])
    link(simplify.outputs[0], frame_end.inputs[0])
    helpers.flush()
    return tree


def show(tree):
    window = bpy.context.window_manager.windows[0]
    view = max(window.screen.areas, key=lambda a: a.width * a.height)
    region = next(r for r in view.regions if r.type == "WINDOW")
    with bpy.context.temp_override(window=window, area=view, region=region):
        bpy.ops.screen.area_split(direction="VERTICAL", factor=0.5)
    views = sorted(
        (a for a in window.screen.areas if a.type == "VIEW_3D"), key=lambda a: a.x
    )
    nodes, viewport = views[0], views[1]
    nodes.type = "NODE_EDITOR"
    space = nodes.spaces.active
    space.tree_type = "ScriptingNodeTree"
    space.node_tree = tree
    space.show_region_ui = False
    viewport.spaces.active.show_region_ui = True
    return window, nodes, viewport


def finish(window, area, viewport):
    region = next(r for r in area.regions if r.type == "WINDOW")
    with bpy.context.temp_override(window=window, area=area, region=region):
        bpy.ops.node.view_all()
    for region in viewport.regions:
        if region.type == "UI":
            try:  # read-only in Blender 5.2
                region.active_panel_category = CATEGORY
            except AttributeError:
                pass


def start():
    try:
        helpers.enable_addon()
        tree = build()
        window, area, viewport = show(tree)
        bpy.app.timers.register(
            lambda: finish(window, area, viewport), first_interval=0.5
        )
        bpy.ops.wm.save_as_mainfile(filepath=OUTPUT)
        errors = helpers.sn("src.core.errors")
        print("ADDON ERROR", errors.addon_error, flush=True)
        print("NODE ERRORS", dict(errors.node_errors), flush=True)
        print("EXAMPLE READY", OUTPUT, flush=True)
    except Exception:
        traceback.print_exc()
        print("EXAMPLE FAILED", flush=True)


bpy.app.timers.register(start, first_interval=0.5)
