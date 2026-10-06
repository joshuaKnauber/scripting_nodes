"""Trigger -> Print: the graph built in "Your first add-on"."""

import helpers

AREA_ONLY = True
WINDOW_SIZE = (900, 480)
ZOOM_OUT = 3


def setup():
    tree = helpers.new_tree("My Addon")
    trigger = helpers.add_node(tree, "SNA_Node_Trigger", (-200, 0))
    printer = helpers.add_node(tree, "SNA_Node_Print", (50, 0))
    printer.inputs[1].value = "Hello!"
    helpers.link(tree, trigger.outputs[0], printer.inputs[0])
    return tree


def after(context):
    # Hide the sidebar so the graph fills the shot
    for area in context.window.screen.areas:
        if area.type == "NODE_EDITOR":
            area.spaces.active.show_region_ui = False
