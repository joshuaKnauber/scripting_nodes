"""A sidebar panel with buttons: Blender's Select All with its Action set, an
operator of the add-on with its Count set, and Shade Smooth without a
label (the operator's own name), next to the node tree."""

import bpy
import helpers

WINDOW_SIZE = (1250, 620)
LAYOUT = "split"
SIDEBAR_TAB = "Scatter"
CROP = (0, 0, 0.835, 0.74)
FRAME = "corner"


def setup():
    bpy.context.scene.sna.addon.addon_name = "Scatter Tools"
    tree = helpers.new_tree("Scatter Panel")

    op = helpers.add_node(tree, "SNA_Node_Operator", (-700, 330))
    op.inputs["label"].value = "Scatter Copies"
    helpers.add_property("Count", "INTEGER", owner=op, default_int=5)

    panel = helpers.add_node(tree, "SNA_Node_Panel", (-700, 60))
    panel.inputs["Label"].value = "Scatter"
    panel.panel_category = "Scatter"

    cube = helpers.add_node(tree, "SNA_Node_Button", (-470, 120))
    cube.mode = "BLENDER"
    cube.operator_blender = "object.select_all"
    helpers.flush()
    cube.inputs["label"].value = "Select All"
    cube.inputs["icon"].value = "RESTRICT_SELECT_OFF"
    cube.socket("arg_action").value = "SELECT"

    scatter = helpers.add_node(tree, "SNA_Node_Button", (-230, 120))
    helpers.point(scatter, "operator_sn", op)
    helpers.flush()
    scatter.inputs["label"].value = "Scatter 10"
    scatter.inputs["icon"].value = "PARTICLES"
    scatter.socket("arg_count").value = 10

    smooth = helpers.add_node(tree, "SNA_Node_Button", (10, 120))
    smooth.mode = "BLENDER"
    smooth.operator_blender = "object.shade_smooth"
    helpers.flush()

    previous = panel.outputs["body"]
    for node in (cube, scatter, smooth):
        node.width = 210
        helpers.link(tree, previous, node.inputs[0])
        previous = node.outputs[0]
    return tree


def after(context):
    for area in context.window_manager.windows[0].screen.areas:
        if area.type == "NODE_EDITOR":
            area.spaces.active.show_region_ui = False
