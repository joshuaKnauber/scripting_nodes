"""A .blend of materials shipped as an asset: an operator appends its
materials, a print lists what's in it."""

import os
import tempfile

import bpy
import helpers

AREA_ONLY = True
WINDOW_SIZE = (1250, 560)
FRAME = "float"


def library():
    """A .blend with a few materials, in a temporary folder."""
    path = os.path.join(tempfile.mkdtemp(), "materials.blend")
    made = [bpy.data.materials.new(name) for name in ("Brass", "Oak", "Rubber")]
    bpy.data.libraries.write(path, set(made), fake_user=True)
    for material in made:
        bpy.data.materials.remove(material)
    return path


def setup():
    asset = bpy.context.scene.sna.addon.assets.add()
    asset.id = helpers.sn("src.lib.ids").get_short_id()
    asset.filepath = library()
    helpers.flush()
    tree = helpers.new_tree("Material Library")
    add = lambda idname, x, y: helpers.add_node(tree, idname, (x, y))  # noqa: E731
    link = lambda a, b: helpers.link(tree, a, b)  # noqa: E731
    op = add("SNA_Node_Operator", -620, 180)
    op.socket("label").value = "Add Materials"
    source = add("SNA_Node_Asset", -620, -150)
    source.asset = "materials.blend"
    load = add("SNA_Node_LoadFromBlend", -300, 180)
    load.data_type = "materials"
    contents = add("SNA_Node_BlendFileContents", -300, -150)
    contents.data_type = "materials"
    printer = add("SNA_Node_Print", 20, 180)
    helpers.flush()
    link(op.outputs["Execute"], load.inputs[0])
    link(source.outputs[0], load.socket("path"))
    link(source.outputs[0], contents.socket("path"))
    link(load.outputs[0], printer.inputs[0])
    link(contents.outputs[0], printer.inputs[1])
    return tree


def after(context):
    for area in context.window_manager.windows[0].screen.areas:
        if area.type == "NODE_EDITOR":
            area.spaces.active.show_region_ui = False
