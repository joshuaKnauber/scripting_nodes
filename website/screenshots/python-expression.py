"""Python Expression with inputs found in the code, and a Python Statement,
in an operator."""

import helpers

AREA_ONLY = True
WINDOW_SIZE = (1050, 470)
FRAME = "float"


def setup():
    tree = helpers.new_tree("Object Tools")
    add = lambda idname, x, y: helpers.add_node(tree, idname, (x, y))  # noqa: E731
    op = add("SNA_Node_Operator", -480, 160)
    op.socket("label").value = "Hide Active"
    data = add("SNA_Node_BlendData", -560, -110)
    data.path = "active_object"
    factor = add("SNA_Node_Float", -480, -290)
    factor.value = 2.0
    expression = add("SNA_Node_PythonExpression", -240, -110)
    expression.code = "round(obj.location.z * factor, 2)"
    helpers.flush()
    printer = add("SNA_Node_Print", 40, 160)
    statement = add("SNA_Node_PythonStatement", 250, 160)
    statement.code = "obj.hide_set(True)"
    helpers.flush()
    link = lambda a, b: helpers.link(tree, a, b)  # noqa: E731
    link(data.outputs[0], expression.inputs["obj"])
    link(factor.outputs[0], expression.inputs["factor"])
    link(op.outputs["Execute"], printer.inputs[0])
    link(expression.outputs[0], printer.inputs["text"])
    link(printer.outputs[0], statement.inputs[0])
    link(data.outputs[0], statement.inputs["obj"])
    return tree


def after(context):
    for area in context.window_manager.windows[0].screen.areas:
        if area.type == "NODE_EDITOR":
            area.spaces.active.show_region_ui = False
