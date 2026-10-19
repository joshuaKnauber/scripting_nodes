"""A small graph with all three flow kinds and shared value nodes: an
operator printing a text, a panel showing it as a label."""

import bpy
import helpers


def build():
    bpy.context.scene.sna.addon.addon_name = "Object Tools"
    tree = helpers.new_tree("Object Tools")
    operator = helpers.add_node(tree, "SNA_Node_Operator", (-560, 260))
    operator.inputs["Label"].value = "Say Hello"
    printer = helpers.add_node(tree, "SNA_Node_Print", (-40, 260))
    math = helpers.add_node(tree, "SNA_Node_Math", (-560, -20))
    math.operation = "MULTIPLY"
    math.inputs["A"].value = 6
    math.inputs["B"].value = 7
    combine = helpers.add_node(tree, "SNA_Node_CombineStrings", (-300, -20))
    combine.inputs["String"].value = "Answer: "
    panel = helpers.add_node(tree, "SNA_Node_Panel", (-560, -250))
    panel.inputs["Label"].value = "Hello"
    label = helpers.add_node(tree, "SNA_Node_Label", (-40, -250))
    helpers.flush()
    helpers.link(tree, operator.outputs["Execute"], printer.inputs[0])
    helpers.link(tree, math.outputs["Integer Result"], combine.socket("string"))
    helpers.link(tree, combine.outputs[0], printer.inputs["Text"])
    helpers.link(tree, panel.outputs["Draw"], label.inputs[0])
    helpers.link(tree, combine.outputs[0], label.inputs["Label"])
    helpers.flush()
    return tree
