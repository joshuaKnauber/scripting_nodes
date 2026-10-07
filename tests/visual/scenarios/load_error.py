"""A Script node with broken Python: the addon keeps its previous version and
the sidebar shows why the new one couldn't load."""

import bpy
import helpers

SIDEBAR_TAB = "Scripting Nodes"


def setup():
    bpy.context.scene.sna.addon.addon_name = "Error Demo"
    tree = helpers.new_tree("Broken")
    trigger = helpers.add_node(tree, "SNA_Node_Trigger", (-300, 0))
    script = helpers.add_node(tree, "SNA_Node_Script", (0, 0))
    text = bpy.data.texts.new("my_script.py")
    text.write("print('works')\n")
    script.text_block = text
    helpers.link(tree, trigger.outputs[0], script.inputs[0])
    helpers.flush()  # loads fine
    text.clear()
    text.write("def broken(:\n    pass\n")
    script.mark_dirty()
    return tree
