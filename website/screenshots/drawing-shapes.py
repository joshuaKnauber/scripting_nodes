"""Draw nodes in the 3D viewport: a filled square, its corner points and a
circle in the scene, a box with text on top."""

import bpy
import helpers

WINDOW_SIZE = (1200, 760)
AREA_ONLY = True
FRAME = "float"

SQUARE = "[(-2.5, -2.5, 0), (2.5, -2.5, 0), (2.5, 2.5, 0), (-2.5, 2.5, 0)]"


def setup():
    bpy.context.scene.sna.addon.addon_name = "Layout Guides"
    tree = helpers.new_tree("Guides")
    add = lambda idname, x, y: helpers.add_node(tree, idname, (x, y))  # noqa: E731
    link = lambda a, b: helpers.link(tree, a, b)  # noqa: E731

    scene = add("SNA_Node_ViewportDraw", 0, 0)
    scene.in_front = True
    corners = add("SNA_Node_PythonExpression", 0, -300)
    corners.code = SQUARE
    polygon = add("SNA_Node_DrawPolygon", 300, 0)
    polygon.socket("color").value = (0.2, 0.8, 1.0, 0.15)
    points = add("SNA_Node_DrawPoints", 500, 0)
    points.socket("color").value = (0.2, 0.8, 1.0, 1.0)
    points.socket("size").value = 14.0
    lines = add("SNA_Node_DrawLines", 700, 0)
    lines.mode = "LINE_LOOP"
    lines.socket("color").value = (0.2, 0.8, 1.0, 1.0)
    circle = add("SNA_Node_DrawCircle", 900, 0)
    circle.socket("radius").value = 1.6
    circle.socket("width").value = 3.0
    circle.socket("segments").value = 64
    circle.socket("color").value = (1.0, 0.75, 0.2, 1.0)

    top = add("SNA_Node_ViewportDraw", 0, -600)
    top.draw_in = "OVERLAY"
    box = add("SNA_Node_DrawRectangle", 300, -600)
    box.socket("position").value[:2] = (20.0, 20.0)
    box.socket("size").value[:2] = (540.0, 100.0)
    box.socket("color").value = (0.0, 0.0, 0.0, 0.6)
    text = add("SNA_Node_DrawText", 500, -600)
    text.socket("text").value = "Safe area: 5 m x 5 m"
    text.socket("position").value[:2] = (48.0, 56.0)
    text.socket("size").value = 18.0
    helpers.flush()

    link(scene.outputs["Draw"], polygon.inputs[0])
    link(polygon.outputs[0], points.inputs[0])
    link(points.outputs[0], lines.inputs[0])
    link(lines.outputs[0], circle.inputs[0])
    for node in (polygon, points, lines):
        link(corners.outputs[0], node.socket("points"))
    link(top.outputs["Draw"], box.inputs[0])
    link(box.outputs[0], text.inputs[0])
    helpers.flush()
    return None  # show the 3D viewport


def after(context):
    for obj in context.view_layer.objects:
        obj.select_set(False)
    for area in context.window_manager.windows[0].screen.areas:
        if area.type == "VIEW_3D":
            space = area.spaces.active
            space.show_region_ui = False
            space.show_region_toolbar = False
            space.region_3d.view_distance = 13.0
            area.tag_redraw()
