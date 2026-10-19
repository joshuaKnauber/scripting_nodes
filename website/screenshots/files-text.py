"""An operator writing the names of the selected objects to a text file next
to the .blend, and printing how many lines the file has."""

import helpers

AREA_ONLY = True
WINDOW_SIZE = (1250, 560)
FRAME = "float"


def setup():
    tree = helpers.new_tree("Selection List")
    add = lambda idname, x, y: helpers.add_node(tree, idname, (x, y))  # noqa: E731
    link = lambda a, b: helpers.link(tree, a, b)  # noqa: E731
    op = add("SNA_Node_Operator", -620, 160)
    op.socket("label").value = "Save Selection"
    names = add("SNA_Node_PythonExpression", -620, -140)
    names.code = '"\\n".join(o.name for o in context.selected_objects)'
    write = add("SNA_Node_WriteTextFile", -250, 160)
    write.socket("path").value = "//selection.txt"
    read = add("SNA_Node_ReadTextFile", -250, -150)
    read.socket("path").value = "//selection.txt"
    length = add("SNA_Node_PythonExpression", 30, -150)
    length.code = "len(lines)"
    helpers.flush()
    printer = add("SNA_Node_Print", 60, 160)
    helpers.flush()
    link(op.outputs["Execute"], write.inputs[0])
    link(names.outputs[0], write.socket("text"))
    link(write.outputs[0], printer.inputs[0])
    link(read.outputs["Lines"], length.inputs["lines"])
    link(length.outputs[0], printer.inputs[1])
    return tree


def after(context):
    for area in context.window_manager.windows[0].screen.areas:
        if area.type == "NODE_EDITOR":
            area.spaces.active.show_region_ui = False
