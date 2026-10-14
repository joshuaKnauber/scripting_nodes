"""A modal operator: header text while it runs, ends with a left click,
clears the header at the end."""

import helpers

AREA_ONLY = True
WINDOW_SIZE = (1300, 620)


def setup():
    tree = helpers.new_tree("Modal")
    add = lambda idname, x, y: helpers.add_node(tree, idname, (x, y))  # noqa: E731
    operator = add("SNA_Node_Operator", -700, 100)
    operator.inputs["Label"].value = "Pick Point"
    operator.invoke_type = "MODAL"
    helpers.flush()
    header = add("SNA_Node_SetHeaderText", -350, 300)
    header.inputs["Text"].value = "Click to pick a point, Esc to cancel"
    key = add("SNA_Node_IsKey", -350, -60)
    branch = add("SNA_Node_IfElse", -50, 120)
    done = add("SNA_Node_OperatorReturn", 250, 160)
    clear = add("SNA_Node_SetHeaderText", -50, -200)
    link = lambda a, b: helpers.link(tree, a, b)  # noqa: E731
    link(operator.outputs["Start"], header.inputs[0])
    link(operator.outputs["Modal"], branch.inputs[0])
    link(operator.outputs["Event"], key.inputs["Event"])
    link(key.outputs[0], branch.inputs["Condition"])
    link(branch.outputs["Then"], done.inputs[0])
    link(operator.outputs["End"], clear.inputs[0])
    return tree


def after(context):
    for area in context.window_manager.windows[0].screen.areas:
        if area.type == "NODE_EDITOR":
            area.spaces.active.show_region_ui = False
