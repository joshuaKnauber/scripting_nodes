"""A Button without an operator: the error on the node and at the top of
the Scripting Nodes sidebar."""

import bpy
import helpers

AREA_ONLY = True
WINDOW_SIZE = (1150, 560)
ZOOM_OUT = 3
CROP = (0, 0, 1, 0.8)
FRAME = "bottom"


def setup():
    bpy.context.scene.sna.addon.addon_name = "Object Tools"
    tree = helpers.new_tree("Object Tools")
    panel = helpers.add_node(tree, "SNA_Node_Panel", (-300, 0))
    panel.inputs["Label"].value = "Object Tools"
    button = helpers.add_node(tree, "SNA_Node_Button", (-40, 0))
    button.inputs["Label"].value = "Arrange"
    button.width = 200
    helpers.flush()
    helpers.link(tree, panel.outputs["Draw"], button.inputs[0])
    helpers.flush()
    return tree


def after(context):
    # nodes framed beside the sidebar, not under it
    context.preferences.system.use_region_overlap = False
