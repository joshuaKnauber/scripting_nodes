"""Show Node Code: every node shows the lines it wrote."""

import bpy
import helpers

AREA_ONLY = True
WINDOW_SIZE = (950, 420)


def setup():
    bpy.context.scene.sna.dev.show_node_code = True
    bpy.context.scene.sna.addon.addon_name = "Object Tools"
    tree = helpers.new_tree("Object Tools")
    operator = helpers.add_node(tree, "SNA_Node_Operator", (-340, 0))
    operator.inputs["Label"].value = "Say Hello"
    operator.width = 300
    printer = helpers.add_node(tree, "SNA_Node_Print", (20, 0))
    printer.inputs["Text"].value = "Hello!"
    printer.width = 220
    helpers.link(tree, operator.outputs["Execute"], printer.inputs[0])
    helpers.flush()
    return tree


def after(context):
    for area in context.window.screen.areas:
        if area.type == "NODE_EDITOR":
            area.spaces.active.show_region_ui = False
