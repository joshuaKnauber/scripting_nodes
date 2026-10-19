"""An operator with Invoke Type File Browser that prints the picked .csv
file, and a File Handler that runs it for .csv files dropped in the 3D
Viewport."""

import os
import sys

import bpy
import helpers

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _operators_common import add, hide_node_sidebar  # noqa: E402

AREA_ONLY = True
WINDOW_SIZE = (950, 460)


def setup():
    bpy.context.scene.sna.addon.addon_name = "CSV Importer"
    tree = helpers.new_tree("Import")
    op = add(tree, "SNA_Node_Operator", (-420, 100))
    op.inputs["Label"].value = "Import CSV"
    op.invoke_type = "FILE_BROWSER"
    op.file_filter = "*.csv"
    helpers.flush()
    printer = add(tree, "SNA_Node_Print", (-170, 100))
    helpers.link(tree, op.outputs["Execute"], printer.inputs[0])
    helpers.link(tree, op.outputs["File Path"], printer.inputs["text"])
    handler = add(tree, "SNA_Node_FileHandler", (-420, -150))
    helpers.point(handler, "operator", op)
    handler.inputs["Label"].value = "CSV Table"
    handler.inputs["Extensions"].value = ".csv"
    return tree


def after(context):
    hide_node_sidebar(context)
