"""Fields for Blender's properties (picked by data path) and a Text Field
in Search style suggesting the names of all objects, next to the panel."""

import bpy
import helpers

WINDOW_SIZE = (1250, 600)
LAYOUT = "split"
SIDEBAR_TAB = "Scatter"
CROP = (0, 0, 0.835, 0.74)
FRAME = "corner"


def setup():
    bpy.context.scene.sna.addon.addon_name = "Scatter Tools"
    target = helpers.add_property("Target", "STRING").id
    tree = helpers.new_tree("Scatter Panel")

    panel = helpers.add_node(tree, "SNA_Node_Panel", (-720, 60))
    panel.inputs["Label"].value = "Scatter"
    panel.panel_category = "Scatter"

    fps = helpers.add_node(tree, "SNA_Node_NumberField", (-480, 120))
    fps.mode = "BLENDER"
    fps.path = "scene.render.fps"
    fps.inputs["text"].value = "Frame Rate"

    names = helpers.add_node(tree, "SNA_Node_Checkbox", (-240, 120))
    names.mode = "BLENDER"
    names.path = "object.show_name"
    names.toggle = True

    search = helpers.add_node(tree, "SNA_Node_TextField", (0, 120))
    search.style = "SEARCH"
    helpers.pick_property(search, helpers.prop(target))
    search.inputs["icon"].value = "OBJECT_DATA"

    objects = helpers.add_node(tree, "SNA_Node_BlendData", (-300, -170))
    objects.path_root = "DATA"
    objects.path = "objects"
    helpers.flush()

    previous = panel.outputs["body"]
    for node in (fps, names, search):
        node.width = 210
        helpers.link(tree, previous, node.inputs[0])
        previous = node.outputs[0]
    helpers.link(tree, objects.outputs[0], search.socket("search"))
    return tree


def after(context):
    group = helpers.sn("src.core.properties").addon_attribute()
    getattr(context.scene, group).target = "Cube"
    for area in context.window_manager.windows[0].screen.areas:
        if area.type == "NODE_EDITOR":
            area.spaces.active.show_region_ui = False
