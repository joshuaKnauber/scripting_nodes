"""Opens GUI Blender to try the data explorer (run by
scripts/open_example.py tests/visual/open_explorer_example.py).

A cube with a few modifiers and materials, a monkey, a tree with a Blender
Data node selected (Active Object) and a Get Property in Blender mode. The
node editor's sidebar shows the Blend Data tab.
"""

import os
import sys
import traceback

import bpy

TESTS_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, TESTS_DIR)

import helpers  # noqa: E402

OUTPUT = sys.argv[sys.argv.index("--") + 1]


def build_scene():
    cube = bpy.data.objects["Cube"]
    cube.modifiers.new("Bevel", "BEVEL")
    cube.modifiers.new("Subdivision", "SUBSURF")
    cube.modifiers.new("Array", "ARRAY")
    for name, color in (("Red", (0.8, 0.1, 0.1, 1)), ("Blue", (0.1, 0.2, 0.8, 1))):
        material = bpy.data.materials.new(name)
        material.diffuse_color = color
        cube.data.materials.append(material)
    bpy.ops.mesh.primitive_monkey_add(location=(3, 0, 0))
    bpy.context.view_layer.objects.active = cube
    cube.select_set(True)


def build():
    build_scene()
    bpy.context.scene.sna.addon.addon_name = "Explorer Example"
    tree = helpers.new_tree("Explorer Example")
    trigger = helpers.add_node(tree, "SNA_Node_Trigger", (-600, 200))
    active = helpers.add_node(tree, "SNA_Node_BlendData", (-600, -50))
    active.path = "active_object"
    printer = helpers.add_node(tree, "SNA_Node_Print", (-150, 200))
    helpers.link(tree, trigger.outputs[0], printer.inputs[0])
    helpers.link(tree, active.outputs[0], printer.inputs[1])
    getter = helpers.add_node(tree, "SNA_Node_GetProperty", (-600, -300))
    getter.mode = "BLENDER"
    getter.path = "scene.frame_end"
    helpers.flush()
    for node in tree.nodes:
        node.select = node == active
    tree.nodes.active = active
    helpers.flush()
    return tree


def show(tree):
    window = bpy.context.window_manager.windows[0]
    view = max(window.screen.areas, key=lambda a: a.width * a.height)
    region = next(r for r in view.regions if r.type == "WINDOW")
    with bpy.context.temp_override(window=window, area=view, region=region):
        bpy.ops.screen.area_split(direction="VERTICAL", factor=0.6)
    views = [a for a in window.screen.areas if a.type == "VIEW_3D"]
    nodes = min(views, key=lambda a: a.x)
    nodes.type = "NODE_EDITOR"
    space = nodes.spaces.active
    space.tree_type = "ScriptingNodeTree"
    space.node_tree = tree
    space.show_region_ui = True
    for region in nodes.regions:
        if region.type == "UI":
            try:
                region.active_panel_category = "Blend Data"
            except Exception:
                pass
    return window, nodes


def frame_all(window, area):
    region = next(r for r in area.regions if r.type == "WINDOW")
    with bpy.context.temp_override(window=window, area=area, region=region):
        bpy.ops.node.view_all()


def start():
    try:
        helpers.enable_addon()
        tree = build()
        window, area = show(tree)
        bpy.app.timers.register(lambda: frame_all(window, area), first_interval=0.5)
        bpy.ops.wm.save_as_mainfile(filepath=OUTPUT)
        print("EXAMPLE READY", OUTPUT, flush=True)
    except Exception:
        traceback.print_exc()
        print("EXAMPLE FAILED", flush=True)


bpy.app.timers.register(start, first_interval=0.5)
