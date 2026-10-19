"""Assets: a file and a folder shipped with the add-on, an Asset node
printing a path."""

import os
import tempfile

import bpy
import helpers


def setup():
    folder = tempfile.mkdtemp()
    os.makedirs(os.path.join(folder, "textures"))
    for rel in ("logo.png", "textures/wood.jpg", "materials.blend"):
        with open(os.path.join(folder, *rel.split("/")), "wb") as f:
            f.write(b"data")
    addon = bpy.context.scene.sna.addon
    for rel in ("logo.png", "textures", "materials.blend"):
        asset = addon.assets.add()
        asset.id = helpers.sn("src.lib.ids").get_short_id()
        asset.filepath = os.path.join(folder, rel)
    addon.active_asset = 2
    tree = helpers.new_tree("Main")
    trigger = helpers.add_node(tree, "SNA_Node_Trigger", (-400, 0))
    node = helpers.add_node(tree, "SNA_Node_Asset", (-420, -200))
    node.asset = "materials.blend"
    p = helpers.add_node(tree, "SNA_Node_Print", (-50, 0))
    helpers.link(tree, trigger.outputs[0], p.inputs[0])
    helpers.link(tree, node.outputs["path"], p.inputs["text"])
    helpers.sn("src.core.scheduler").request_full()
    helpers.flush()
    return tree
