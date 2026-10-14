"""Python Expression with inputs found in the code, and a Python Statement."""

import helpers

AREA_ONLY = True
WINDOW_SIZE = (1200, 520)


def setup():
    tree = helpers.new_tree("Python")
    add = lambda idname, x, y: helpers.add_node(tree, idname, (x, y))  # noqa: E731
    trigger = add("SNA_Node_Trigger", -650, 150)
    data = add("SNA_Node_BlendData", -700, -80)
    data.path = "active_object"
    factor = add("SNA_Node_Float", -650, -300)
    factor.value = 2.0
    expression = add("SNA_Node_PythonExpression", -330, -60)
    expression.code = "round(obj.location.z * factor, 2)"
    helpers.flush()
    printer = add("SNA_Node_Print", 30, 150)
    statement = add("SNA_Node_PythonStatement", 300, 150)
    statement.code = "obj.hide_set(True)"
    helpers.flush()
    helpers.link(tree, data.outputs[0], expression.inputs["obj"])
    helpers.link(tree, factor.outputs[0], expression.inputs["factor"])
    helpers.link(tree, trigger.outputs[0], printer.inputs[0])
    helpers.link(tree, expression.outputs[0], printer.inputs["text"])
    helpers.link(tree, printer.outputs[0], statement.inputs[0])
    helpers.link(tree, data.outputs[0], statement.inputs["obj"])
    return tree


def after(context):
    for area in context.window_manager.windows[0].screen.areas:
        if area.type == "NODE_EDITOR":
            area.spaces.active.show_region_ui = False
