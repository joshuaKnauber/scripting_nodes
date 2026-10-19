"""A Global Variable counting button clicks, shown in a sidebar panel."""

import bpy
import helpers

WINDOW_SIZE = (1150, 560)
LAYOUT = "split"
SIDEBAR_TAB = "Object Tools"
CROP = (0, 0, 0.855, 0.85)
FRAME = "corner"
INTEGER = "ScriptingIntegerSocket"


def setup():
    bpy.context.scene.sna.addon.addon_name = "Object Tools"
    tree = helpers.new_tree("Object Tools")
    add = lambda idname, x, y: helpers.add_node(tree, idname, (x, y))  # noqa: E731
    count = add("SNA_Node_GlobalVariable", -940, 160)
    count.label = "Click Count"
    count.data_type = INTEGER
    operator = add("SNA_Node_Operator", -720, 160)
    operator.inputs["label"].value = "Count Click"
    change = add("SNA_Node_SetVariable", -500, 160)
    change.operation = "ADD"
    panel = add("SNA_Node_Panel", -940, -60)
    panel.inputs["label"].value = "Object Tools"
    get = add("SNA_Node_GetVariable", -940, -300)
    text = add("SNA_Node_CombineStrings", -720, -200)
    text.inputs["first"].value = "Clicks: "
    label = add("SNA_Node_Label", -500, -60)
    button = add("SNA_Node_Button", -280, -60)
    helpers.flush()
    helpers.point(change, "var", count)
    helpers.point(get, "var", count)
    helpers.flush()
    change.inputs["Amount"].value = 1
    link = lambda a, b: helpers.link(tree, a, b)  # noqa: E731
    link(operator.outputs["execute"], change.inputs[0])
    link(panel.outputs["Draw"], label.inputs[0])
    link(get.outputs[0], text.socket("string"))
    link(text.outputs[0], label.inputs["text"])
    link(label.outputs[0], button.inputs[0])
    helpers.flush()
    helpers.point(button, "operator_sn", operator)
    button.inputs["label"].value = "Count Click"
    helpers.flush()
    for node in tree.nodes:
        node.select = False
    return tree


def after(context):
    for area in context.window_manager.windows[0].screen.areas:
        if area.type == "NODE_EDITOR":
            area.spaces.active.show_region_ui = False
    for _ in range(3):
        bpy.ops.object_tools.count_click()
