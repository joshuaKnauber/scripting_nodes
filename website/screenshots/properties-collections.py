"""Collection nodes on a collection property (Entries, items of the group
Entry): an operator adding an entry and naming it, one removing the first
entry, one clearing the list."""

import os
import sys

import bpy
import helpers

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
import _blend_data_zoom  # noqa: E402

AREA_ONLY = True
WINDOW_SIZE = (1000, 560)


def setup():
    bpy.context.scene.sna.addon.addon_name = "Notes"
    entry = helpers.add_property("Entry", "GROUP").id
    label = helpers.add_property(
        "Label", "STRING", owner=helpers.prop(entry), default_string="Entry"
    ).id
    entries = helpers.add_property("Entries", "COLLECTION").id
    helpers.prop(entries).group_id = entry
    tree = helpers.new_tree("Notes")
    add = lambda idname, x, y: helpers.add_node(tree, idname, (x, y))  # noqa: E731
    link = lambda a, b: helpers.link(tree, a, b)  # noqa: E731

    get = add("SNA_Node_GetProperty", -330, -110)
    helpers.pick_property(get, helpers.prop(entries))

    op_add = add("SNA_Node_Operator", -560, 110)
    op_add.inputs["label"].value = "Add Entry"
    new = add("SNA_Node_CollectionAdd", -40, 110)
    set_label = add("SNA_Node_SetProperty", 180, 110)
    helpers.pick_property(set_label, helpers.prop(label))
    helpers.flush()
    set_label.socket("value").value = "New note"
    link(op_add.outputs["Execute"], new.inputs[0])
    link(get.outputs["Value"], new.inputs["Collection"])
    link(new.outputs[0], set_label.inputs[0])
    link(new.outputs["New Item"], set_label.socket("data"))

    op_remove = add("SNA_Node_Operator", -560, -300)
    op_remove.inputs["label"].value = "Remove First"
    remove = add("SNA_Node_CollectionRemove", -40, -300)
    link(op_remove.outputs["Execute"], remove.inputs[0])
    link(get.outputs["Value"], remove.inputs["Collection"])
    helpers.flush()
    return tree


def after(context):
    _blend_data_zoom.zoom_in(context, steps=3)
