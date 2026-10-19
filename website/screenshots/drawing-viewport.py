"""Viewport drawing: the active object outlined in the scene and its name
drawn on top, next to the 3D viewport showing the result."""

import bpy
import helpers

WINDOW_SIZE = (1500, 820)
LAYOUT = "split"
CROP = (0, 0, 0.8, 0.86)  # not the properties editor or timeline
FRAME = "corner"


def blend_data(tree, location, path):
    node = helpers.add_node(tree, "SNA_Node_BlendData", location)
    node.path = path
    return node


def setup():
    bpy.context.scene.sna.addon.addon_name = "Object Labels"
    tree = helpers.new_tree("Object Labels")
    add = lambda idname, x, y: helpers.add_node(tree, idname, (x, y))  # noqa: E731
    link = lambda a, b: helpers.link(tree, a, b)  # noqa: E731

    obj = blend_data(tree, (-980, 220), "active_object")
    outline = add("SNA_Node_ViewportDraw", -700, 380)
    outline.label = "Outline"
    outline.in_front = True
    wire = add("SNA_Node_DrawObject", -420, 380)
    wire.socket("color").value = (0.2, 0.8, 1.0, 1.0)
    wire.socket("width").value = 3.0

    label = add("SNA_Node_ViewportDraw", -700, 100)
    label.label = "Name"
    label.draw_in = "OVERLAY"
    text = add("SNA_Node_DrawText", -420, 100)
    text.align = "CENTER"
    text.shadow = True
    text.socket("size").value = 22.0
    name = blend_data(tree, (-980, -10), "active_object.name")
    where = blend_data(tree, (-980, -170), "active_object.location")
    above = add("SNA_Node_PythonExpression", -700, -120)
    above.code = "location + mathutils.Vector((0, 0, 1.6))"
    helpers.flush()
    screen = add("SNA_Node_LocationToScreen", -420, -200)
    helpers.flush()

    link(outline.outputs["Draw"], wire.inputs[0])
    link(obj.outputs[0], wire.socket("object"))
    link(label.outputs["Draw"], text.inputs[0])
    link(name.outputs[0], text.socket("text"))
    link(where.outputs[0], above.inputs["location"])
    link(above.outputs[0], screen.socket("location"))
    link(screen.socket("position", output=True), text.socket("position"))
    helpers.flush()
    return tree


def after(context):
    for obj in context.view_layer.objects:
        obj.select_set(False)  # the drawn outline, not the selection's
    for area in context.window_manager.windows[0].screen.areas:
        if area.type == "NODE_EDITOR":
            area.spaces.active.show_region_ui = False
        if area.type == "VIEW_3D":
            space = area.spaces.active
            space.show_region_ui = False
            space.show_region_toolbar = False
            space.region_3d.view_distance = 9.0
            area.tag_redraw()
