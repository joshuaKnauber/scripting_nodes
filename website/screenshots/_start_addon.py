"""The add-on of the Start guide: an Add Monkey operator running Blender's
Add Monkey, and a sidebar panel with a button for it."""

import bpy
import helpers


def build(with_panel=True):
    bpy.context.scene.sna.addon.addon_name = "Monkey Tools"
    tree = helpers.new_tree("Monkey Tools")
    operator = helpers.add_node(tree, "SNA_Node_Operator", (-280, 0))
    operator.width = 190
    operator.inputs["Label"].value = "Add Monkey"
    run = helpers.add_node(tree, "SNA_Node_RunOperator", (0, 0))
    run.mode = "BLENDER"
    run.operator_blender = "mesh.primitive_monkey_add"
    helpers.flush()
    helpers.link(tree, operator.outputs["Execute"], run.inputs[0])
    if not with_panel:
        helpers.flush()
        return tree
    panel = helpers.add_node(tree, "SNA_Node_Panel", (-280, 270))
    panel.width = 190
    panel.inputs["Label"].value = "Monkeys"
    button = helpers.add_node(tree, "SNA_Node_Button", (0, 270))
    helpers.flush()
    helpers.link(tree, panel.outputs["Draw"], button.inputs[0])
    helpers.point(button, "operator_sn", operator)
    helpers.flush()
    return tree
