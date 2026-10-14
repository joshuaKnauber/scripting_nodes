"""A UI List of the file's objects with their icons, in a sidebar panel."""

import bpy
import helpers

WINDOW_SIZE = (1600, 760)
LAYOUT = "split"
SIDEBAR_TAB = "Objects"


def setup():
    bpy.context.scene.sna.addon.addon_name = "List Demo"
    index = helpers.add_property("Active Index", "INTEGER")
    tree = helpers.new_tree("Lists")
    add = lambda idname, x, y: helpers.add_node(tree, idname, (x, y))  # noqa: E731
    panel = add("SNA_Node_Panel", -800, 100)
    panel.inputs["Label"].value = "Objects"
    panel.panel_category = "Objects"
    ui_list = add("SNA_Node_UIList", -500, 100)
    ui_list.label = "Objects"
    objects = add("SNA_Node_BlendData", -800, -200)
    objects.path_root = "DATA"
    objects.path = "objects"
    label = add("SNA_Node_Label", -150, 150)
    icon = add("SNA_Node_IconFromData", -150, -150)
    helpers.flush()
    link = lambda a, b: helpers.link(tree, a, b)  # noqa: E731
    link(panel.outputs["Interface"], ui_list.inputs[0])
    link(objects.outputs[0], ui_list.inputs["Items"])
    helpers.pick_property(ui_list, helpers.prop(index.id))
    item = ui_list.socket("item_data", output=True)
    link(ui_list.outputs[0], label.inputs[0])
    link(item, label.inputs["text"])
    link(item, icon.inputs["Data"])
    link(icon.outputs[0], label.inputs["icon"])
    return tree


def after(context):
    for area in context.window_manager.windows[0].screen.areas:
        if area.type == "NODE_EDITOR":
            area.spaces.active.show_region_ui = False
