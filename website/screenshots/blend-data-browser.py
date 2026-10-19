"""The path browser open on a Blender Data node: the active object's
Bevel modifier, its properties with their current values."""

import bpy
import helpers

WINDOW_SIZE = (1300, 690)
CROP = (0, 0, 0.852, 1)
FRAME = "right"


def setup():
    cube = bpy.data.objects.get("Cube")
    if cube is not None and "Bevel" not in cube.modifiers:
        bevel = cube.modifiers.new("Bevel", "BEVEL")
        bevel.width = 0.08
        bevel.segments = 3
    tree = helpers.new_tree("Object Tools")
    node = helpers.add_node(tree, "SNA_Node_BlendData", (0, 0))
    node.path = "active_object.modifiers[]"
    node.path_keys[0].mode = "NAME"
    node.socket("key_0").value = "Bevel"
    helpers.flush()
    return tree


def after(context):
    window = context.window_manager.windows[0]
    area = max(
        (a for a in window.screen.areas if a.type == "NODE_EDITOR"),
        key=lambda a: a.width * a.height,
    )
    area.spaces.active.show_region_ui = False
    region = next(r for r in area.regions if r.type == "WINDOW")
    node = area.spaces.active.node_tree.nodes[0]

    def open_browser():
        with context.temp_override(window=window, area=area, region=region):
            bpy.ops.sna.browse_path("INVOKE_DEFAULT", node_id=node.id)

    # the dialog opens with its Use Path button at the mouse: near the bottom
    window.cursor_warp(window.width // 2, 40)
    bpy.app.timers.register(open_browser, first_interval=2.3)
