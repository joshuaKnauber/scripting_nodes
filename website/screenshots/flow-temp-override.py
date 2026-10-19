"""Temp Override running View All in the 3D viewport from anywhere."""

import helpers

AREA_ONLY = True
WINDOW_SIZE = (1000, 460)


def setup():
    tree = helpers.new_tree("Viewport Tools")
    add = lambda idname, x, y: helpers.add_node(tree, idname, (x, y))  # noqa: E731
    trigger = add("SNA_Node_Trigger", -480, 120)
    area = add("SNA_Node_AreaByType", -480, -40)
    override = add("SNA_Node_TempOverride", -230, 120)
    run = add("SNA_Node_RunOperator", 30, 160)
    run.mode = "BLENDER"
    run.operator_blender = "view3d.view_all"
    done = add("SNA_Node_Print", 30, -60)
    done.inputs["Text"].value = "Framed the scene"
    run.width = done.width = 230
    helpers.flush()
    link = lambda a, b: helpers.link(tree, a, b)  # noqa: E731
    link(trigger.outputs[0], override.inputs[0])
    link(area.outputs["Area"], override.inputs["Area"])
    link(area.outputs["Region"], override.inputs["Region"])
    link(override.outputs["During"], run.inputs[0])
    link(override.outputs["After"], done.inputs[0])
    for node in tree.nodes:
        node.select = False
    return tree


def after(context):
    for area in context.window_manager.windows[0].screen.areas:
        if area.type == "NODE_EDITOR":
            area.spaces.active.show_region_ui = False
