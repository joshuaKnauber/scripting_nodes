"""Shared builder of the interface pages: an "Object Tools" add-on with a
sidebar panel in the 3D Viewport (fields of the active object, a row of
buttons, a subpanel)."""

import bpy
import helpers


def blender_operator(idname):
    operator_call = helpers.sn("src.nodes._operator_call")
    return next(
        display
        for display, bl_idname in operator_call.blender_operator_choices()
        if bl_idname == idname
    )


def add(tree, idname, location, **settings):
    node = helpers.add_node(tree, idname, location)
    for name, value in settings.items():
        setattr(node, name, value)
    return node


def button(tree, location, operator, label, icon):
    node = add(tree, "SNA_Node_Button", location, mode="BLENDER")
    node.operator_blender = blender_operator(operator)
    helpers.flush()
    node.inputs["label"].value = label
    node.inputs["icon"].value = icon
    return node


def build():
    """The Object Tools tree; returns (tree, nodes by name)."""
    bpy.context.scene.sna.addon.addon_name = "Object Tools"
    tree = helpers.new_tree("Object Tools")
    blender = {"mode": "BLENDER"}
    panel = add(tree, "SNA_Node_Panel", (-560, 0))
    panel.inputs["Label"].value = "Object Tools"
    row = add(tree, "SNA_Node_Row", (-390, 0))
    smooth = button(tree, (-220, 200), "object.shade_smooth", "Smooth", "MOD_SMOOTH")
    flat = button(tree, (-60, 200), "object.shade_flat", "Flat", "MESH_CUBE")
    sub = add(tree, "SNA_Node_Subpanel", (-220, -90))
    sub.label = "Display"
    title = add(tree, "SNA_Node_Label", (-60, -40))
    name = add(tree, "SNA_Node_Checkbox", (-60, -180), path="object.show_name", **blender)
    helpers.flush()
    title.inputs["text"].value = "Display"
    row.inputs["Align"].value = True
    link = lambda a, b: helpers.link(tree, a, b)  # noqa: E731
    link(panel.outputs["Draw"], row.inputs[0])
    link(row.outputs["Row"], smooth.inputs[0])
    link(smooth.outputs[0], flat.inputs[0])
    link(row.outputs["After"], sub.inputs[0])
    link(sub.outputs["Header"], title.inputs[0])
    link(sub.outputs["Panel"], name.inputs[0])
    nodes = dict(panel=panel, row=row, subpanel=sub)
    return tree, nodes


def hide_node_sidebar(context):
    for area in context.window_manager.windows[0].screen.areas:
        if area.type == "NODE_EDITOR":
            area.spaces.active.show_region_ui = False


