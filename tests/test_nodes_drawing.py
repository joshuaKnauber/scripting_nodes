"""Viewport drawing (nodes/categories/drawing, DRAW_HELPERS in core/helpers.py).
Drawing itself needs a GPU (the GUI), these check the generated code."""

import unittest

import bpy
import helpers


def errors():
    return helpers.sn("src.core.errors")


class DrawingNodesTest(unittest.TestCase):
    def setUp(self):
        helpers.reset_file()
        bpy.context.scene.sna.addon.addon_name = "Draw Test"
        self.tree = helpers.new_tree("Drawing")

    def tearDown(self):
        for tree in list(bpy.data.node_groups):
            bpy.data.node_groups.remove(tree)

    def add(self, idname, after=None):
        node = helpers.add_node(self.tree, idname)
        helpers.flush()
        if after is not None:
            helpers.link(self.tree, after, node.inputs[0])
        return node

    def source(self):
        helpers.flush()
        self.assertIsNone(errors().addon_error)
        return helpers.tree_source(self.tree)

    def test_draw_in_the_scene(self):
        draw = self.add("SNA_Node_ViewportDraw")
        lines = self.add("SNA_Node_DrawLines", draw.outputs[0])
        lines.mode = "LINE_LOOP"
        lines.socket("width").value = 4.0
        source = self.source()
        for expected in (
            "def draw_viewport():",
            'gpu.state.blend_set("ALPHA")',
            'gpu.state.depth_test_set("LESS_EQUAL")',  # hidden behind objects
            "utils.draw_lines([], width=4.0, mode='LINE_LOOP')",  # color is default
            "utils.add_draw_handler(bpy.types.SpaceView3D, draw_viewport, 'POST_VIEW')",
        ):
            self.assertIn(expected, source)
        utils = helpers.addon_files().get("utils.py", "")
        self.assertIn("def draw_lines(", utils)
        self.assertIn("def _batch(", utils)  # what draw_lines calls
        self.assertIn("draw_handler_remove", utils)

    def test_on_top_with_enabled(self):
        draw = self.add("SNA_Node_ViewportDraw")
        draw.draw_in = "OVERLAY"
        draw.editor = "IMAGE_EDITOR"
        flag = self.add("SNA_Node_Boolean")
        helpers.link(self.tree, flag.outputs[0], draw.socket("enabled"))
        text = self.add("SNA_Node_DrawText", draw.outputs[0])
        text.align = "CENTER"
        text.shadow = True
        source = self.source()
        self.assertIn("if not ", source)
        self.assertNotIn("depth_test_set", source)
        self.assertIn("SpaceImageEditor, draw_viewport, 'POST_PIXEL'", source)
        self.assertIn(
            "utils.draw_text('Text', (20.0, 20.0), align='CENTER', shadow=True)", source
        )

    def test_every_shape(self):
        draw = self.add("SNA_Node_ViewportDraw")
        last = draw.outputs[0]
        for idname in (
            "SNA_Node_DrawPoints",
            "SNA_Node_DrawPolygon",
            "SNA_Node_DrawRectangle",
            "SNA_Node_DrawCircle",
            "SNA_Node_DrawImage",
            "SNA_Node_DrawObject",
        ):
            last = self.add(idname, last).outputs[0]
        source = self.source()
        for call in (
            "utils.draw_points([])",
            "utils.draw_polygon([])",
            "utils.draw_rectangle((20.0, 20.0), (200.0, 100.0))",
            "utils.draw_circle((0.0, 0.0, 0.0), 1.0)",
            "utils.draw_image(None, (20.0, 20.0), (128.0, 128.0))",
            "utils.draw_object(None)",
        ):
            self.assertIn(call, source)

    def test_screen_conversions(self):
        draw = self.add("SNA_Node_ViewportDraw")
        draw.draw_in = "OVERLAY"
        text = self.add("SNA_Node_DrawText", draw.outputs[0])
        where = self.add("SNA_Node_LocationToScreen")
        helpers.link(self.tree, where.outputs[0], text.socket("position"))
        source = self.source()
        self.assertIn("from bpy_extras import view3d_utils", source)
        self.assertIn(
            "view3d_utils.location_3d_to_region_2d(bpy.context.region, bpy.context.region_data",
            source,
        )


if __name__ == "__main__":
    unittest.main()
