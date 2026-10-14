"""A Pie Menu with three buttons (shading and framing), opened with Shift Q in the 3D Viewport."""

import helpers

AREA_ONLY = True
WINDOW_SIZE = (1300, 760)


def blender_operator(idname):
    operator_call = helpers.sn("src.nodes._operator_call")
    return next(
        display
        for display, bl_idname in operator_call.blender_operator_choices()
        if bl_idname == idname
    )


def button(tree, location, operator, label, icon):
    node = helpers.add_node(tree, "SNA_Node_Button", location)
    node.mode = "BLENDER"
    node.operator_blender = blender_operator(operator)
    helpers.flush()
    node.inputs["label"].value = label
    node.inputs["icon"].value = icon
    return node


def setup():
    tree = helpers.new_tree("Pie")
    pie = helpers.add_node(tree, "SNA_Node_PieMenu", (-500, 100))
    pie.inputs["Label"].value = "Quick View"
    smooth = button(tree, (-150, 330), "object.shade_smooth", "Smooth", "MOD_SMOOTH")
    flat = button(tree, (-150, 30), "object.shade_flat", "Flat", "MESH_CUBE")
    frame = button(tree, (-150, -270), "view3d.view_selected", "Frame", "ZOOM_SELECTED")
    helpers.link(tree, pie.outputs["Left"], smooth.inputs[0])
    helpers.link(tree, pie.outputs["Right"], flat.inputs[0])
    helpers.link(tree, pie.outputs["Top"], frame.inputs[0])
    shortcut = helpers.add_node(tree, "SNA_Node_Shortcut", (250, 100))
    shortcut.action = "MENU"
    helpers.point(shortcut, "menu", pie)
    shortcut.key = "Q"
    shortcut.shift = True
    shortcut.keymap = "3D View"
    return tree


def after(context):
    for area in context.window_manager.windows[0].screen.areas:
        if area.type == "NODE_EDITOR":
            area.spaces.active.show_region_ui = False
