"""Trigger -> Print -> Print, with node code preview on."""

import bpy
import helpers


def setup():
    bpy.context.scene.sna.dev.show_node_code = True
    tree = helpers.new_tree("Demo")
    trigger = helpers.add_node(tree, "SNA_Node_Trigger", (-400, 0))
    p1 = helpers.add_node(tree, "SNA_Node_Print", (-100, 0))
    p2 = helpers.add_node(tree, "SNA_Node_Print", (250, 0))
    p1.inputs[1].value = "Hello"
    p2.inputs[1].value = "World"
    helpers.link(tree, trigger.outputs[0], p1.inputs[0])
    helpers.link(tree, p1.outputs[0], p2.inputs[0])
    return tree
