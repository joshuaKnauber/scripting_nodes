"""Assets: a file, a folder and a .blend in Addon Data > Assets, an Asset
node printing the path of one."""

import os
import tempfile

import bpy
import helpers

AREA_ONLY = True
WINDOW_SIZE = (1150, 800)
ZOOM_OUT = 1


def setup():
    folder = tempfile.mkdtemp()
    os.makedirs(os.path.join(folder, "textures"))
    for rel in ("logo.png", "textures/wood.jpg", "materials.blend"):
        with open(os.path.join(folder, *rel.split("/")), "wb") as f:
            f.write(b"data")
    addon = bpy.context.scene.sna.addon
    addon.addon_name = "Object Tools"
    for rel in ("logo.png", "textures", "materials.blend"):
        asset = addon.assets.add()
        asset.id = helpers.sn("src.lib.ids").get_short_id()
        asset.filepath = os.path.join(folder, rel)
    addon.active_asset = 2
    tree = helpers.new_tree("Object Tools")
    trigger = helpers.add_node(tree, "SNA_Node_Trigger", (-260, 60))
    node = helpers.add_node(tree, "SNA_Node_Asset", (-300, -140))
    node.asset = "materials.blend"
    p = helpers.add_node(tree, "SNA_Node_Print", (20, 60))
    helpers.link(tree, trigger.outputs[0], p.inputs[0])
    helpers.link(tree, node.outputs["Path"], p.inputs["Text"])
    helpers.sn("src.core.scheduler").request_full()
    helpers.flush()
    return tree


def _scroll_sidebar():
    """Scroll the sidebar down to Addon Data (once it has drawn)."""
    window = bpy.context.window_manager.windows[0]
    for area in window.screen.areas:
        if area.type != "NODE_EDITOR":
            continue
        region = next(r for r in area.regions if r.type == "UI")
        with bpy.context.temp_override(window=window, area=area, region=region):
            for _ in range(20):
                bpy.ops.view2d.scroll_down()
        region.tag_redraw()
    return None


def after(context):
    context.preferences.system.use_region_overlap = False
    bpy.app.timers.register(_scroll_sidebar, first_interval=1.0)
