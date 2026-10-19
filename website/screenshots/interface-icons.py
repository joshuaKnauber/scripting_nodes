"""Icons: a picked built-in icon, the Icon node, a Custom Icon from an
image, Icon from Data (the active object's icon) and Display Icon drawing
the custom icon large, in a live panel next to the node tree."""

import os
import tempfile

import bpy
import helpers

WINDOW_SIZE = (1350, 680)
LAYOUT = "split"
SIDEBAR_TAB = "Icons"
CROP = (0, 0, 0.845, 0.78)
FRAME = "corner"


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
    panel = helpers.add_node(tree, "SNA_Node_Panel", (-960, 100))
    panel.inputs["Label"].value = "Icons"
    panel.panel_category = "Icons"

    def label(text, x):
        node = helpers.add_node(tree, "SNA_Node_Label", (x, 150))
        node.inputs["text"].value = text
        return node

    picked = label("Built-in icon", -740)
    picked.inputs["icon"].value = "MESH_MONKEY"
    from_node = label("From the Icon node", -540)
    data_label = label("Active object", -340)
    custom_label = label("Custom icon", -140)
    display = helpers.add_node(tree, "SNA_Node_DisplayIcon", (60, 150))
    display.inputs["Scale"].value = 3.0

    icon = helpers.add_node(tree, "SNA_Node_Icon", (-560, -100))
    icon.icon = "SHADING_RENDERED"
    custom = helpers.add_node(tree, "SNA_Node_CustomIcon", (-100, -100))
    custom.image = _image()
    from_data = helpers.add_node(tree, "SNA_Node_IconFromData", (-340, -100))
    active = helpers.add_node(tree, "SNA_Node_BlendData", (-600, -260))
    active.path = "object"

    previous = panel.outputs["body"]
    for node in (picked, from_node, data_label, custom_label, display):
        helpers.link(tree, previous, node.inputs[0])
        previous = node.outputs[0]
    helpers.link(tree, icon.outputs[0], from_node.inputs["icon"])
    helpers.link(tree, custom.outputs[0], custom_label.inputs["icon"])
    helpers.link(tree, custom.outputs[0], display.inputs["icon"])
    helpers.link(tree, active.outputs[0], from_data.inputs[0])
    helpers.link(tree, from_data.outputs[0], data_label.inputs["icon"])
    return tree


def after(context):
    # the node editor's sidebar would cover the nodes
    for area in context.window_manager.windows[0].screen.areas:
        if area.type == "NODE_EDITOR":
            area.spaces.active.show_region_ui = False
