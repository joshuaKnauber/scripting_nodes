"""An operator that reports now, again after two seconds, and counts down
in intervals."""

import helpers

AREA_ONLY = True
WINDOW_SIZE = (1300, 560)


def setup():
    tree = helpers.new_tree("Timers")
    add = lambda idname, x, y: helpers.add_node(tree, idname, (x, y))  # noqa: E731
    operator = add("SNA_Node_Operator", -700, 100)
    operator.inputs["Label"].value = "Start Countdown"
    delay = add("SNA_Node_RunWithDelay", -400, 100)
    delay.inputs["Seconds"].value = 2.0
    later = add("SNA_Node_Print", -100, 220)
    later.inputs["Text"].value = "Two seconds later"
    intervals = add("SNA_Node_RunInIntervals", -100, -20)
    intervals.inputs["Times"].value = 3
    format_ = add("SNA_Node_FormatString", 180, -220)
    format_.inputs["Format"].value = "Tick {}"
    tick = add("SNA_Node_Print", 450, 60)
    helpers.link(tree, operator.outputs["Execute"], delay.inputs[0])
    helpers.link(tree, delay.outputs["Delayed"], later.inputs[0])
    helpers.link(tree, delay.socket("next", output=True), intervals.inputs[0])
    helpers.link(tree, intervals.outputs["Repeat"], tick.inputs[0])
    helpers.link(tree, intervals.outputs["Index"], format_.inputs[-1])
    helpers.link(tree, format_.outputs[0], tick.inputs["text"])
    return tree


def after(context):
    # the node editor's sidebar would cover the nodes
    for area in context.window_manager.windows[0].screen.areas:
        if area.type == "NODE_EDITOR":
            area.spaces.active.show_region_ui = False
