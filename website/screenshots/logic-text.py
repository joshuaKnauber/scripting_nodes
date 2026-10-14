"""String nodes: Format String with a padded number, Split String and
Join List, printed by a Trigger."""

import helpers

AREA_ONLY = True
WINDOW_SIZE = (1300, 560)


def setup():
    tree = helpers.new_tree("Text")
    add = lambda idname, x, y: helpers.add_node(tree, idname, (x, y))  # noqa: E731
    trigger = add("SNA_Node_Trigger", -650, 120)
    number = add("SNA_Node_Integer", -650, -120)
    number.value = 7
    pad = add("SNA_Node_PadString", -420, -60)
    format_ = add("SNA_Node_FormatString", -170, -20)
    format_.inputs["Format"].value = "Shot_{}.png"
    printer = add("SNA_Node_Print", 120, 120)
    split = add("SNA_Node_SplitString", -170, -330)
    split.inputs["String"].value = "red green blue"
    join = add("SNA_Node_JoinList", 120, -260)
    join.inputs["Separator"].value = " / "
    printer_2 = add("SNA_Node_Print", 380, 120)
    helpers.link(tree, number.outputs[0], pad.inputs["String"])
    helpers.link(tree, pad.outputs[0], format_.inputs[-1])
    helpers.link(tree, trigger.outputs[0], printer.inputs[0])
    helpers.link(tree, format_.outputs[0], printer.inputs["text"])
    helpers.link(tree, split.outputs[0], join.inputs["List"])
    helpers.link(tree, printer.outputs[0], printer_2.inputs[0])
    helpers.link(tree, join.outputs[0], printer_2.inputs["text"])
    return tree


def after(context):
    # the node editor's sidebar would cover the nodes
    for area in context.window_manager.windows[0].screen.areas:
        if area.type == "NODE_EDITOR":
            area.spaces.active.show_region_ui = False
