"""Two shortcuts: Ctrl Shift G runs an operator in the 3D Viewport, Alt Q
opens a menu everywhere."""

import helpers

AREA_ONLY = True
WINDOW_SIZE = (900, 560)


def setup():
    tree = helpers.new_tree("Shortcuts")
    add = lambda idname, x, y: helpers.add_node(tree, idname, (x, y))  # noqa: E731
    operator = add("SNA_Node_Operator", -500, 150)
    operator.inputs["Label"].value = "Greet"
    printer = add("SNA_Node_Print", -290, 150)
    printer.inputs["Text"].value = "Hello"
    helpers.link(tree, operator.outputs["Execute"], printer.inputs[0])
    shortcut = add("SNA_Node_Shortcut", -70, 170)
    helpers.point(shortcut, "operator_sn", operator)
    shortcut.key = "G"
    shortcut.ctrl = shortcut.shift = True
    shortcut.keymap = "3D View"
    panel = add("SNA_Node_Panel", -500, -90)
    panel.inputs["Label"].value = "Tools"
    menu = add("SNA_Node_Menu", -290, -90)
    menu.inputs["Label"].value = "Quick Tools"
    helpers.link(tree, panel.outputs["Draw"], menu.inputs[0])
    menu_shortcut = add("SNA_Node_Shortcut", -70, -50)
    menu_shortcut.action = "MENU"
    helpers.point(menu_shortcut, "menu", menu)
    menu_shortcut.key = "Q"
    menu_shortcut.alt = True
    return tree


def after(context):
    # the node editor's sidebar would cover the nodes
    for area in context.window_manager.windows[0].screen.areas:
        if area.type == "NODE_EDITOR":
            area.spaces.active.show_region_ui = False
