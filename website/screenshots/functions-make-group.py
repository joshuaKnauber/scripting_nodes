"""Ctrl+G on Combine Strings and Print: the new function with Group Input /
Output for the links that crossed the selection."""

import bpy
import helpers

AREA_ONLY = True
WINDOW_SIZE = (1300, 640)


def setup():
    tree = helpers.new_tree("Main")
    trigger = helpers.add_node(tree, "SNA_Node_Trigger", (-500, 0))
    name = helpers.add_node(tree, "SNA_Node_String", (-500, -200))
    name.value = "World"
    combine = helpers.add_node(tree, "SNA_Node_CombineStrings", (-200, -200))
    combine.inputs["first"].value = "Hello, "
    say = helpers.add_node(tree, "SNA_Node_Print", (100, 0))
    done = helpers.add_node(tree, "SNA_Node_Print", (400, 0))
    done.inputs["text"].value = "done"
    helpers.link(tree, trigger.outputs[0], say.inputs[0])
    helpers.link(tree, name.outputs[0], combine.socket("string"))
    helpers.link(tree, combine.outputs[0], say.inputs["text"])
    helpers.link(tree, say.outputs[0], done.inputs[0])
    for node in tree.nodes:
        node.select = node in (combine, say)
    return tree


def after(context):
    area = next(a for a in context.window.screen.areas if a.type == "NODE_EDITOR")
    area.spaces.active.show_region_ui = False
    region = next(r for r in area.regions if r.type == "WINDOW")
    with context.temp_override(
        area=area, region=region, space_data=area.spaces.active
    ):
        bpy.ops.sna.make_group()
