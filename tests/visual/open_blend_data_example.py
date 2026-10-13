"""Opens GUI Blender on a Blend Data example (run by scripts/open_example.py).

The example add-on: a sidebar panel in the 3D viewport with Blender
properties drawn through data paths, and an operator that reads typed
Blender data (active object, its mesh, a collection length) and sets a
property.
"""

import os
import sys
import traceback

import bpy

TESTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TESTS_DIR)

import helpers  # noqa: E402

OUTPUT = sys.argv[sys.argv.index("--") + 1]


def ref(node):
    return helpers.sn("src.core.references").display_name(node)


def blend_data(tree, location, path, root="CONTEXT"):
    node = helpers.add_node(tree, "SNA_Node_BlendData", location)
    node.path_root = root
    node.path = path
    return node


def build():
    cube = bpy.data.objects.get("Cube")
    if cube is not None and "Bevel" not in cube.modifiers:
        cube.modifiers.new("Bevel", "BEVEL")
    bpy.context.scene.sna.addon.addon_name = "Blend Data Example"
    tree = helpers.new_tree("Blend Data Example")
    link = lambda a, b: helpers.link(tree, a, b)  # noqa: E731

    # -- operator: report the active object ---------------------------------
    op = helpers.add_node(tree, "SNA_Node_Operator", (-900, 500))
    op.socket("label").value = "Report Active Object"

    active = blend_data(tree, (-900, 200), "active_object")
    name = blend_data(tree, (-600, 200), "name", root="INPUT")
    link(active.outputs[0], name.socket("data"))

    mesh = blend_data(tree, (-900, -50), "active_object.data")
    mesh.path_cast = "Mesh"
    vertices = blend_data(tree, (-600, -50), "vertices", root="INPUT")
    link(mesh.outputs[0], vertices.socket("data"))
    count = helpers.add_node(tree, "SNA_Node_CollectionLength", (-300, -50))
    link(vertices.outputs[0], count.inputs[0])

    print_name = helpers.add_node(tree, "SNA_Node_Print", (-300, 450))
    print_count = helpers.add_node(tree, "SNA_Node_Print", (0, 450))
    show_name = helpers.add_node(tree, "SNA_Node_SetProperty", (300, 450))
    show_name.mode = "BLENDER"
    show_name.path = "active_object.show_name"
    show_name.socket("value").value = True
    link(op.outputs["Execute"], print_name.inputs[0])
    link(name.outputs[0], print_name.inputs[1])
    link(print_name.outputs[0], print_count.inputs[0])
    link(count.outputs[0], print_count.inputs[1])
    link(print_count.outputs[0], show_name.inputs[0])

    # -- panel in the 3D viewport sidebar -----------------------------------
    panel = helpers.add_node(tree, "SNA_Node_Panel", (-900, -400))
    panel.socket("label").value = "Blend Data Example"
    simplify = helpers.add_node(tree, "SNA_Node_Checkbox", (-600, -400))
    simplify.mode = "BLENDER"
    simplify.path = "scene.render.use_simplify"
    frame_end = helpers.add_node(tree, "SNA_Node_NumberField", (-350, -400))
    frame_end.mode = "BLENDER"
    frame_end.path = "scene.frame_end"
    bevel = helpers.add_node(tree, "SNA_Node_NumberField", (-100, -400))
    bevel.mode = "BLENDER"
    # what "Copy Data Path for Scripting Nodes" puts on the clipboard
    bevel.paste_path('bpy.data.objects["Cube"].modifiers["Bevel"].width')
    button = helpers.add_node(tree, "SNA_Node_Button", (200, -400))
    button.operator_sn = ref(op)
    link(panel.outputs["Interface"], simplify.inputs[0])
    link(simplify.socket("next", output=True), frame_end.inputs[0])
    link(frame_end.socket("next", output=True), bevel.inputs[0])
    link(bevel.socket("next", output=True), button.inputs[0])
    helpers.flush()
    return tree


def show(tree):
    window = bpy.context.window_manager.windows[0]
    area = max(window.screen.areas, key=lambda a: a.width * a.height)
    region = next(r for r in area.regions if r.type == "WINDOW")
    with bpy.context.temp_override(window=window, area=area, region=region):
        bpy.ops.screen.area_split(direction="VERTICAL", factor=0.62)
    views = [a for a in window.screen.areas if a.type == "VIEW_3D"]
    left = min(views, key=lambda a: a.x)
    right = max(views, key=lambda a: a.x)
    right.spaces.active.show_region_ui = True
    left.type = "NODE_EDITOR"
    space = left.spaces.active
    space.tree_type = "ScriptingNodeTree"
    space.node_tree = tree
    space.show_region_ui = False
    for region in right.regions:
        if region.type == "UI":
            try:
                region.active_panel_category = "Scripting Nodes"
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
        tree = build()
        window, area = show(tree)
        bpy.app.timers.register(lambda: frame(window, area), first_interval=0.5)
        bpy.ops.wm.save_as_mainfile(filepath=OUTPUT)
        print("EXAMPLE READY", OUTPUT)
    except Exception:
        traceback.print_exc()
        print("EXAMPLE FAILED")


bpy.app.timers.register(start, first_interval=0.5)
