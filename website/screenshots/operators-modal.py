"""A modal operator that changes the frame while the mouse moves: header
text and cursor at the start, a left click finishes, the header and cursor
are reset at the end."""

import os
import sys

import bpy
import helpers

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from _operators_common import add, hide_node_sidebar  # noqa: E402

AREA_ONLY = True
WINDOW_SIZE = (1000, 600)


def build():
    bpy.context.scene.sna.addon.addon_name = "Timeline Tools"
    tree = helpers.new_tree("Scrub Frames")
    op = add(tree, "SNA_Node_Operator", (-720, 100))
    op.inputs["Label"].value = "Scrub Frames"
    op.invoke_type = "MODAL"
    helpers.flush()
    link = lambda a, b: helpers.link(tree, a, b)  # noqa: E731

    header = add(tree, "SNA_Node_SetHeaderText", (-540, 360))
    header.inputs["Text"].value = "Move the mouse to change the frame, click to confirm"
    cursor = add(tree, "SNA_Node_SetCursor", (-350, 360), cursor="SCROLL_X")
    link(op.outputs["Start"], header.inputs[0])
    link(header.outputs[0], cursor.inputs[0])

    branch = add(tree, "SNA_Node_IfElse", (-350, 200))
    key = add(tree, "SNA_Node_IsKey", (-540, 200))
    done = add(tree, "SNA_Node_OperatorReturn", (-160, 250), result="FINISHED")
    link(op.outputs["Modal"], branch.inputs[0])
    link(op.outputs["Event"], key.inputs["Event"])
    link(key.outputs[0], branch.inputs["Condition"])
    link(branch.outputs["Then"], done.inputs[0])

    info = add(tree, "SNA_Node_EventInfo", (-540, -10))
    split = add(tree, "SNA_Node_SeparateVector", (-350, -80))
    frame = add(tree, "SNA_Node_BlendData", (-350, 40), path_root="CONTEXT")
    frame.path = "scene.frame_current"
    helpers.flush()
    frame.width = 180
    plus = add(tree, "SNA_Node_Math", (-160, 20))
    store = add(tree, "SNA_Node_SetProperty", (30, 160), mode="BLENDER")
    store.path_root = "CONTEXT"
    store.path = "scene.frame_current"
    helpers.flush()
    link(op.outputs["Event"], info.inputs["Event"])
    link(info.outputs["Mouse Offset"], split.inputs[0])
    link(frame.outputs[0], plus.inputs["A"])
    link(split.outputs["X"], plus.inputs["B"])
    link(branch.outputs["Else"], store.inputs[0])
    link(plus.outputs["Integer Result"], store.inputs["Value"])

    clear = add(tree, "SNA_Node_SetHeaderText", (-540, -250))
    reset = add(tree, "SNA_Node_SetCursor", (-350, -250), cursor="DEFAULT")
    link(op.outputs["End"], clear.inputs[0])
    link(clear.outputs[0], reset.inputs[0])
    helpers.flush()
    for socket in info.outputs:  # only Mouse Offset is used
        socket.hide = socket.name != "Mouse Offset"
    return tree, op


def setup():
    tree, _ = build()
    return tree


def after(context):
    hide_node_sidebar(context)
