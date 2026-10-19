"""The Scripting Nodes sidebar: add-on status, name and the Files list with
folders, node trees and a script."""

import bpy
import helpers

AREA_ONLY = True
WINDOW_SIZE = (1100, 820)
CROP = (0.62, 0.0, 1.0, 0.719)
FRAME = "right"


def setup():
    bpy.context.scene.sna.addon.addon_name = "Object Tools"
    main = helpers.new_tree("Object Tools")
    panels = helpers.new_tree("Object Panel")
    panels.folder = "UI"
    ops = helpers.new_tree("Arrange")
    ops.folder = "Operators"
    text = bpy.data.texts.new("helpers.py")
    text.write("def spacing(count):\n    return count * 2.0\n")
    helpers.add_script(text)
    helpers.sn("src.core.scheduler").request_full()
    helpers.flush()
    return main


def after(context):
    helpers.sn("src.node_tree.file_list").sync(context.scene)
    rows = context.scene.sna.ui.files
    for i, row in enumerate(rows):
        if row.kind == "TREE":
            tree = next(t for t in bpy.data.node_groups if getattr(t, "id", "") == row.item_id)
            if tree.name == "Object Panel":
                context.scene.sna.ui.active_file = i
