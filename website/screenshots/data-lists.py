"""Lists: an operator collects the names of the selected objects in a list
(Local Variable, For Each (List), List Append) and reports them joined
(Join List)."""

import helpers

AREA_ONLY = True
WINDOW_SIZE = (940, 500)
CROP = (0, 0, 0.94, 0.95)
FRAME = "corner"


def setup():
    tree = helpers.new_tree("Selection Report")
    add = lambda idname, x, y: helpers.add_node(tree, idname, (x, y))  # noqa: E731
    link = lambda a, b: helpers.link(tree, a, b)  # noqa: E731
    operator = add("SNA_Node_Operator", -800, 140)
    operator.inputs["Label"].value = "Report Selection"
    helpers.flush()
    names = add("SNA_Node_LocalVariable", -600, 140)
    names.label = "Names"
    names.data_type = "ScriptingListSocket"
    helpers.flush()
    selected = helpers.add_node(tree, "SNA_Node_BlendData", (-640, -110))
    selected.path_root = "CONTEXT"
    selected.path = "selected_objects"
    loop = add("SNA_Node_ForEachList", -380, 140)
    name = helpers.add_node(tree, "SNA_Node_BlendData", (-380, -130))
    name.path_root = "INPUT"
    name.path = "name"
    append = add("SNA_Node_ListAppend", -110, 40)
    join = add("SNA_Node_JoinList", -110, 300)
    report = add("SNA_Node_Report", 120, 300)
    helpers.flush()

    link(operator.outputs["Execute"], names.inputs[0])
    link(names.socket("next", output=True), loop.inputs[0])
    link(selected.outputs[0], loop.inputs["List"])
    link(loop.outputs["Loop"], append.inputs[0])
    link(names.outputs["Value"], append.inputs["List"])
    link(loop.outputs["Item"], name.socket("data"))
    link(name.outputs[0], append.inputs["Item"])
    link(loop.socket("next", output=True), report.inputs[0])
    link(names.outputs["Value"], join.inputs["List"])
    link(join.outputs[0], report.inputs["Message"])
    helpers.flush()
    return tree


def after(context):
    for area in context.window_manager.windows[0].screen.areas:
        if area.type == "NODE_EDITOR":
            area.spaces.active.show_region_ui = False
