"""A Panel node with labels and a button: the generated panel shows up live
in the 3D viewport sidebar next to the node tree."""

import bpy
import helpers

LAYOUT = "split"


def setup():
    bpy.context.scene.sna.addon.addon_name = "Demo Addon"
    tree = helpers.new_tree("Interface")
    panel = helpers.add_node(tree, "SNA_Node_Panel", (-500, 0))
    panel.inputs["Label"].value = "Made with Serpens"
    l1 = helpers.add_node(tree, "SNA_Node_Label", (-150, 100))
    l1.inputs[1].value = "Hello from a node tree"
    l2 = helpers.add_node(tree, "SNA_Node_Label", (150, 100))
    l2.inputs[1].value = "Edits reload live"
    helpers.link(tree, panel.outputs["Interface"], l1.inputs[0])
    helpers.link(tree, l1.outputs[0], l2.inputs[0])
    return tree


def after(context):
    # the panel's tab is "Scripting Nodes" by default
    pass
