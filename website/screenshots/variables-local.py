"""A Local Variable adding up the index of a Repeat, printed after the loop."""

import bpy
import helpers

AREA_ONLY = True
WINDOW_SIZE = (1050, 480)
INTEGER = "ScriptingIntegerSocket"


def setup():
    bpy.context.scene.sna.addon.addon_name = "Object Tools"
    tree = helpers.new_tree("Object Tools")
    add = lambda idname, x, y: helpers.add_node(tree, idname, (x, y))  # noqa: E731
    trigger = add("SNA_Node_Trigger", -700, 60)
    total = add("SNA_Node_LocalVariable", -500, 60)
    total.label = "Total"
    total.data_type = INTEGER
    repeat = add("SNA_Node_Repeat", -280, 60)
    repeat.inputs["Times"].value = 5
    change = add("SNA_Node_SetVariable", -50, 140)
    change.operation = "ADD"
    get = add("SNA_Node_GetVariable", -280, -150)
    printer = add("SNA_Node_Print", -50, -60)
    helpers.flush()
    helpers.point(change, "var", total)
    helpers.point(get, "var", total)
    helpers.flush()
    link = lambda a, b: helpers.link(tree, a, b)  # noqa: E731
    link(trigger.outputs[0], total.inputs[0])
    link(total.outputs[0], repeat.inputs[0])
    link(repeat.outputs["Loop"], change.inputs[0])
    link(repeat.outputs["Index"], change.inputs["Amount"])
    link(repeat.socket("next", output=True), printer.inputs[0])
    link(get.outputs[0], printer.inputs["Text"])
    for node in tree.nodes:
        node.select = False
    return tree


def after(context):
    for area in context.window_manager.windows[0].screen.areas:
        if area.type == "NODE_EDITOR":
            area.spaces.active.show_region_ui = False
    context.scene.sna.dev.log_overlay_font_size = 24
    bpy.ops.object_tools.trigger()  # prints 0 + 1 + 2 + 3 + 4
