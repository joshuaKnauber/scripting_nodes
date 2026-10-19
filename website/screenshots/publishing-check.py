"""Addon › Extensions Platform listing what reviewers would ask to change,
for an operator that breaks a few guidelines."""

import os
import sys

import bpy

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _publishing  # noqa: E402
import helpers  # noqa: E402

AREA_ONLY = True
WINDOW_SIZE = (1000, 760)
CROP = (0.663, 0, 1, 0.925)  # the sidebar, down to Export Addon
FRAME = "float"


def setup():
    _publishing.open_panels("SNA_PT_Export_Check")
    _publishing.build()
    bpy.context.scene.sna.addon.author = ""  # missing metadata too
    tree = helpers.new_tree("Presets")
    op = helpers.add_node(tree, "SNA_Node_Operator", (-600, 200))
    op.socket("label").value = "Save Preset"
    cube = helpers.add_node(tree, "SNA_Node_BlendData", (-600, -100))
    cube.paste_path('bpy.data.objects["Cube"].location')
    printer = helpers.add_node(tree, "SNA_Node_Print", (-300, 200))
    statement = helpers.add_node(tree, "SNA_Node_PythonStatement", (0, 200))
    statement.code = "context.window_manager.clipboard = 'copied'"
    helpers.flush()
    helpers.link(tree, op.outputs["Execute"], printer.inputs[0])
    helpers.link(tree, cube.outputs[0], printer.socket("text"))
    helpers.link(tree, printer.outputs[0], statement.inputs[0])
    helpers.flush()
    helpers.sn("src.core.export_check").run()
    return tree
