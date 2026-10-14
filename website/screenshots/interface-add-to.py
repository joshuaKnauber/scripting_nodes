"""Add to Panel: a label and a button drawn into the Object properties'
Transform panel, next to the node tree."""

import bpy
import helpers

WINDOW_SIZE = (1600, 800)


def blender_operator(idname):
    operator_call = helpers.sn("src.nodes._operator_call")
    return next(
        display
        for display, bl_idname in operator_call.blender_operator_choices()
        if bl_idname == idname
    )


def setup():
    bpy.context.scene.sna.addon.addon_name = "Transform Extras"
    tree = helpers.new_tree("Extras")
    add = lambda idname, x, y: helpers.add_node(tree, idname, (x, y))  # noqa: E731
    add_to = add("SNA_Node_AddToPanel", -650, 100)
    add_to.target = "Transform  [OBJECT_PT_transform]"
    separator = add("SNA_Node_Separator", -380, 100)
    label = add("SNA_Node_Label", -150, 100)
    label.inputs["text"].value = "Transform Extras"
    label.inputs["icon"].value = "PLUGIN"
    button = add("SNA_Node_Button", 100, 100)
    button.mode = "BLENDER"
    button.operator_blender = blender_operator("object.transform_apply")
    helpers.flush()
    button.inputs["label"].value = "Apply Transforms"
    button.inputs["icon"].value = "CHECKMARK"
    helpers.link(tree, add_to.outputs[0], separator.inputs[0])
    helpers.link(tree, separator.outputs[0], label.inputs[0])
    helpers.link(tree, label.outputs[0], button.inputs[0])
    return tree


def after(context):
    for area in context.window_manager.windows[0].screen.areas:
        if area.type == "NODE_EDITOR":
            area.spaces.active.show_region_ui = False
