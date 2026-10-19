"""Repeat with a Switch on the index: skip one run, stop at another."""

import helpers

AREA_ONLY = True
WINDOW_SIZE = (1300, 600)


def setup():
    tree = helpers.new_tree("Loops")
    add = lambda idname, x, y: helpers.add_node(tree, idname, (x, y))  # noqa: E731
    trigger = add("SNA_Node_Trigger", -750, 100)
    repeat = add("SNA_Node_Repeat", -500, 100)
    repeat.inputs["Times"].value = 10
    switch = add("SNA_Node_Switch", -200, 160)
    switch.cases[0].value = "3"
    switch.cases[1].value = "7"
    skip = add("SNA_Node_LoopControl", 150, 330)
    skip.action = "continue"
    stop = add("SNA_Node_LoopControl", 150, 180)
    printer = add("SNA_Node_Print", 150, 20)
    done = add("SNA_Node_Print", -200, -220)
    done.inputs["Text"].value = "Done"
    helpers.link(tree, trigger.outputs[0], repeat.inputs[0])
    helpers.link(tree, repeat.outputs["Loop"], switch.inputs[0])
    helpers.link(tree, repeat.outputs["Index"], switch.inputs["Value"])
    helpers.link(tree, switch.outputs["3"], skip.inputs[0])
    helpers.link(tree, switch.outputs["7"], stop.inputs[0])
    helpers.link(tree, switch.socket("next", output=True), printer.inputs[0])
    helpers.link(tree, repeat.outputs["Index"], printer.inputs["text"])
    helpers.link(tree, repeat.socket("next", output=True), done.inputs[0])
    return tree


def after(context):
    for area in context.window_manager.windows[0].screen.areas:
        if area.type == "NODE_EDITOR":
            area.spaces.active.show_region_ui = False
