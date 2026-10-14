"""Icons: a picked built-in icon, the Icon node and a Custom Icon from an
image, drawn in a live panel next to the node tree."""

import os
import tempfile

import bpy
import helpers

WINDOW_SIZE = (1600, 800)
LAYOUT = "split"
SIDEBAR_TAB = "Icons"


def _image():
    size = 32
    image = bpy.data.images.new("Logo", size, size)
    pixels = []
    for y in range(size):
        for x in range(size):
            inside = (x - 15.5) ** 2 + (y - 15.5) ** 2 < 14**2
            pixels += [1.0, 0.45, 0.1, 1.0] if inside else [0.0, 0.0, 0.0, 0.0]
    image.pixels = pixels
    image.filepath_raw = os.path.join(tempfile.mkdtemp(), "logo.png")
    image.file_format = "PNG"
    image.save()
    image.source = "FILE"
    return image


def setup():
    bpy.context.scene.sna.addon.addon_name = "Icon Demo"
    tree = helpers.new_tree("Interface")
    panel = helpers.add_node(tree, "SNA_Node_Panel", (-1000, 100))
    panel.inputs["Label"].value = "Icons"
    panel.panel_category = "Icons"
    label = helpers.add_node(tree, "SNA_Node_Label", (-750, 150))
    label.inputs["text"].value = "Built-in icon"
    label.inputs["icon"].value = "MESH_MONKEY"
    icon = helpers.add_node(tree, "SNA_Node_Icon", (-750, -150))
    icon.icon = "SHADING_RENDERED"
    second = helpers.add_node(tree, "SNA_Node_Label", (-500, 150))
    second.inputs["text"].value = "From the Icon node"
    custom = helpers.add_node(tree, "SNA_Node_CustomIcon", (-500, -150))
    custom.image = _image()
    third = helpers.add_node(tree, "SNA_Node_Label", (-250, 150))
    third.inputs["text"].value = "Custom icon"
    helpers.link(tree, panel.outputs["body"], label.inputs[0])
    helpers.link(tree, label.outputs[0], second.inputs[0])
    helpers.link(tree, icon.outputs[0], second.inputs["icon"])
    helpers.link(tree, second.outputs[0], third.inputs[0])
    helpers.link(tree, custom.outputs[0], third.inputs["icon"])
    return tree


def after(context):
    # the node editor's sidebar would cover the nodes
    for area in context.window_manager.windows[0].screen.areas:
        if area.type == "NODE_EDITOR":
            area.spaces.active.show_region_ui = False
