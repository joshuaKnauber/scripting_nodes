"""Make Group (Ctrl+G) on two selected nodes: the editor opens the new
function, with Group Input / Output for the links that crossed the selection."""

import bpy
import helpers

ZOOM_OUT = 1


def setup():
    bpy.context.scene.sna.addon.addon_name = "Make Group Demo"
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
    window = context.window_manager.windows[0]
    area = next(a for a in window.screen.areas if a.type == "NODE_EDITOR")
    region = next(r for r in area.regions if r.type == "WINDOW")
    with context.temp_override(
        window=window, area=area, region=region, space_data=area.spaces.active
    ):
        bpy.ops.sna.make_group()
