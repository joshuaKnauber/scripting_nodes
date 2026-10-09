"""A small add-on built on property lists, shared by the properties
scenarios:

    add-on properties   Enabled, Count, Mode, Entries (collection of Entry)
    group Entry         Label, Weight
    operator Add Entry  its own property Weight; adds an entry with it
    panel               fields for Enabled / Count / Mode, the Add Entry
                        button and the number of entries
    On Property Update  prints when Count changes
"""

import bpy
import helpers


def build():
    bpy.context.scene.sna.addon.addon_name = "Properties Demo"
    # ids: adding to a list can move earlier items (helpers.prop)
    enabled = helpers.add_property("Enabled", "BOOLEAN", default_bool=True).id
    count = helpers.add_property(
        "Count", "INTEGER", default_int=3, use_soft_limits=True, soft_max=10
    ).id
    mode = helpers.add_property("Mode", "ENUM")
    mode.enum_items[0].name = "Fast"
    mode.enum_items[1].name = "Precise"
    mode = mode.id
    entry = helpers.add_property("Entry", "GROUP").id
    helpers.add_property(
        "Label", "STRING", owner=helpers.prop(entry), default_string="Entry"
    )
    weight = helpers.add_property(
        "Weight", "FLOAT", owner=helpers.prop(entry), default_float=1.0
    ).id
    entries = helpers.add_property("Entries", "COLLECTION").id
    helpers.prop(entries).group_id = entry
    bpy.context.scene.sna.addon.active_property = 1

    tree = helpers.new_tree("Main")
    op = helpers.add_node(tree, "SNA_Node_Operator", (-900, 350))
    op.inputs["label"].value = "Add Entry"
    op_weight = helpers.add_property("Weight", "FLOAT", owner=op, default_float=0.5).id
    get_entries = helpers.add_node(tree, "SNA_Node_GetProperty", (-650, 150))
    helpers.pick_property(get_entries, helpers.prop(entries))
    add = helpers.add_node(tree, "SNA_Node_CollectionAdd", (-400, 350))
    set_weight = helpers.add_node(tree, "SNA_Node_SetProperty", (-150, 350))
    helpers.pick_property(set_weight, helpers.prop(weight))
    helpers.link(tree, op.outputs["Execute"], add.inputs[0])
    helpers.link(tree, get_entries.outputs["Value"], add.inputs["Collection"])
    helpers.link(tree, add.outputs[0], set_weight.inputs[0])
    helpers.link(tree, add.outputs["New Item"], set_weight.socket("data"))
    helpers.link(tree, op.outputs["prop_" + op_weight], set_weight.socket("value"))

    panel = helpers.add_node(tree, "SNA_Node_Panel", (-900, -200))
    panel.inputs["label"].value = "Properties Demo"
    fields = []
    for idname, prop, x in (
        ("SNA_Node_Checkbox", enabled, -650),
        ("SNA_Node_NumberField", count, -400),
        ("SNA_Node_EnumMenu", mode, -150),
    ):
        field = helpers.add_node(tree, idname, (x, -200))
        helpers.pick_property(field, helpers.prop(prop))
        fields.append(field)
    fields[2].expand = True
    button = helpers.add_node(tree, "SNA_Node_Button", (100, -200))
    button.operator_sn = helpers.sn("src.core.references").display_name(op)
    length = helpers.add_node(tree, "SNA_Node_CollectionLength", (100, -450))
    text = helpers.add_node(tree, "SNA_Node_CombineStrings", (350, -450))
    text.inputs["first"].value = "Entries: "
    label = helpers.add_node(tree, "SNA_Node_Label", (350, -200))
    previous = panel.outputs["body"]
    for node in fields + [button, label]:
        helpers.link(tree, previous, node.inputs[0])
        previous = node.outputs[0]
    helpers.link(tree, get_entries.outputs["Value"], length.inputs[0])
    helpers.link(tree, length.outputs[0], text.socket("string"))
    helpers.link(tree, text.outputs[0], label.inputs["text"])

    update = helpers.add_node(tree, "SNA_Node_OnPropertyUpdate", (-900, 700))
    helpers.pick_property(update, helpers.prop(count))
    say = helpers.add_node(tree, "SNA_Node_Print", (-600, 700))
    helpers.link(tree, update.outputs[0], say.inputs[0])
    helpers.link(tree, update.outputs["Value"], say.inputs["text"])
    helpers.flush()
    return tree, op
