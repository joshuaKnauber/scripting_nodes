"""An Inline Script in an operator: its free name `amount` is an input, the
variable `moved` an output."""

import bpy
import helpers

AREA_ONLY = True
WINDOW_SIZE = (1050, 470)
FRAME = "float"

CODE = """for obj in context.selected_objects:
    obj.location.z += amount
moved = len(context.selected_objects)
"""


def setup():
    text = bpy.data.texts.new("lift.py")
    text.write(CODE)
    tree = helpers.new_tree("Object Tools")
    add = lambda idname, x, y: helpers.add_node(tree, idname, (x, y))  # noqa: E731
    op = add("SNA_Node_Operator", -480, 160)
    op.socket("label").value = "Lift Selected"
    amount = add("SNA_Node_Float", -480, -120)
    amount.value = 0.5
    script = add("SNA_Node_InlineScript", -230, 160)
    script.text_block = text
    script.output_names = "moved"
    helpers.flush()
    printer = add("SNA_Node_Print", 60, 160)
    helpers.flush()
    link = lambda a, b: helpers.link(tree, a, b)  # noqa: E731
    link(op.outputs["Execute"], script.inputs[0])
    link(amount.outputs[0], script.inputs["amount"])
    link(script.outputs[0], printer.inputs[0])
    link(script.outputs["moved"], printer.inputs["text"])
    return tree


def after(context):
    for area in context.window_manager.windows[0].screen.areas:
        if area.type == "NODE_EDITOR":
            area.spaces.active.show_region_ui = False
