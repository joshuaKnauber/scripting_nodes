"""Trigger -> Print: trying a flow from the Start guide. The Trigger was
clicked, the overlay shows the printed message."""

import bpy
import helpers

AREA_ONLY = True
WINDOW_SIZE = (800, 360)
ZOOM_OUT = 2


def setup():
    bpy.context.scene.sna.addon.addon_name = "Monkey Tools"
    tree = helpers.new_tree("Monkey Tools")
    trigger = helpers.add_node(tree, "SNA_Node_Trigger", (-220, 0))
    printer = helpers.add_node(tree, "SNA_Node_Print", (20, 0))
    printer.inputs["Text"].value = "It works!"
    printer.width = 180
    helpers.link(tree, trigger.outputs[0], printer.inputs[0])
    return tree


def after(context):
    for area in context.window.screen.areas:
        if area.type == "NODE_EDITOR":
            area.spaces.active.show_region_ui = False
    tree = bpy.data.node_groups["Monkey Tools"]
    trigger = next(n for n in tree.nodes if n.bl_idname == "SNA_Node_Trigger")
    category, name = trigger.operator_idname.split(".")
    getattr(getattr(bpy.ops, category), name)()
