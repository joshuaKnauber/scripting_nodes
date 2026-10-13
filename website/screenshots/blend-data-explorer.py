"""The data explorer at the active object's Bevel modifier, with a Blender
Data node selected."""

import bpy
import helpers

WINDOW_SIZE = (1600, 1000)
SIDEBAR_TAB = "Blend Data"


def setup():
    cube = bpy.data.objects["Cube"]
    cube.modifiers.new("Bevel", "BEVEL")
    cube.modifiers.new("Subdivision", "SUBSURF")
    bpy.context.view_layer.objects.active = cube
    tree = helpers.new_tree("Explorer")
    trigger = helpers.add_node(tree, "SNA_Node_Trigger", (-500, 0))
    node = helpers.add_node(tree, "SNA_Node_BlendData", (-250, -150))
    node.path = "active_object.modifiers[]"
    node.path_keys[0].mode = "NAME"
    node.socket("key_0").value = "Bevel"
    printer = helpers.add_node(tree, "SNA_Node_Print", (100, 0))
    helpers.link(tree, trigger.outputs[0], printer.inputs[0])
    helpers.link(tree, node.outputs[0], printer.inputs[1])
    for other in tree.nodes:
        other.select = other == node
    tree.nodes.active = node
    bpy.context.scene.sna.ui.explorer_path = (
        "bpy.context.active_object.modifiers['Bevel']"
    )
    helpers.flush()
    return tree
