"""A Trigger running a Print: the message shows in the node editor."""

import bpy
import helpers

AREA_ONLY = True
WINDOW_SIZE = (900, 420)


def setup():
    bpy.context.scene.sna.addon.addon_name = "Object Tools"
    tree = helpers.new_tree("Object Tools")
    trigger = helpers.add_node(tree, "SNA_Node_Trigger", (-250, 0))
    printer = helpers.add_node(tree, "SNA_Node_Print", (0, 0))
    helpers.flush()
    helpers.link(tree, trigger.outputs[0], printer.inputs[0])
    printer.inputs["Text"].value = "Hello from Object Tools"
    printer.width = 240
    for node in tree.nodes:
        node.select = False
    return tree


def after(context):
    for area in context.window_manager.windows[0].screen.areas:
        if area.type == "NODE_EDITOR":
            area.spaces.active.show_region_ui = False
    context.scene.sna.dev.log_overlay_font_size = 26
    # what pressing Trigger does: the Print node logs to the overlay
    try:
        bpy.ops.object_tools.trigger()
    except Exception as exc:
        print("TRIGGER FAILED", exc)
        bpy.app.driver_namespace["_sn_overlay_log"]("INFO", "Hello from Object Tools")
