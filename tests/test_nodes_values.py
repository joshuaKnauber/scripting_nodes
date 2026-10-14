"""Value nodes (vectors, angles, random, time, mode, object type, areas,
icons from data, add-on info) and the flow nodes Repeat, Break / Continue,
Switch and Redraw."""

import os

import bpy
import helpers
from flow_case import FlowTestCase, errors


class ValueNodesTest(FlowTestCase):
    addon_name = "Value Test"

    def setUp(self):
        super().setUp()
        mesh = bpy.data.meshes.new("Cube")
        bpy.context.scene.collection.objects.link(bpy.data.objects.new("Cube", mesh))

    def test_combine_and_separate_vector(self):
        combine = self.add("SNA_Node_CombineVector")
        combine.dimension = "2"
        helpers.flush()
        self.assertEqual([s.name for s in combine.inputs], ["X", "Y"])
        combine.socket("x").value, combine.socket("y").value = 1.0, 2.0
        separate = self.add("SNA_Node_SeparateVector")
        separate.dimension = "2"
        self.link(combine.outputs["vector"], separate.socket("vector"))
        self.print_value(separate.outputs["y"])
        self.print_value(combine.outputs["vector"])
        self.assertEqual(self.run_trigger(), ["2.0", "(1.0, 2.0)"])

    def test_angle_and_random(self):
        angle = self.add("SNA_Node_ConvertAngle")
        angle.conversion = "degrees"
        angle.socket("angle").value = 3.14159265
        self.print_value(angle.outputs["angle"])
        rand = self.add("SNA_Node_RandomValue")
        rand.data_type = "INTEGER"
        helpers.flush()
        rand.socket("min").value = rand.socket("max").value = 4
        self.print_value(rand.outputs["value"])
        color = self.add("SNA_Node_RandomValue")
        color.data_type = "COLOR"
        helpers.flush()
        self.print_value(color.outputs["value"])
        degrees, number, rgb = self.run_trigger()
        self.assertAlmostEqual(float(degrees), 180.0, places=3)
        self.assertEqual(number, "4")
        self.assertEqual(len(eval(rgb)), 3)

    def test_time(self):
        time_node = self.add("SNA_Node_CurrentTime")
        time_node.socket("format").value = "%Y"
        self.print_value(time_node.outputs["text"])
        (year,) = self.run_trigger()
        import time

        self.assertEqual(year, time.strftime("%Y"))

    def test_mode_type_and_area(self):
        mode = self.add("SNA_Node_IsInMode")
        self.print_value(mode.outputs["is_in_mode"])
        self.print_value(mode.outputs["mode"])
        obj = self.add("SNA_Node_PythonExpression")
        obj.code = "bpy.data.objects['Cube']"
        helpers.flush()
        is_type = self.add("SNA_Node_IsObjectType")
        self.link(obj.outputs["result"], is_type.socket("object"))
        self.print_value(is_type.outputs["is_type"])
        nothing = self.add("SNA_Node_IsObjectType")  # no object: False
        self.print_value(nothing.outputs["is_type"])
        area = self.add("SNA_Node_AreaByType")
        self.print_value(area.outputs["found"])
        self.print_value(area.outputs["region"])
        lines = self.run_trigger()
        self.assertEqual(lines[:4], ["True", "OBJECT", "True", "False"])
        self.assertEqual(lines[4], "True")  # the home file's 3D Viewport
        self.assertIn("Region", lines[5])

    def test_icon_from_data(self):
        icon = self.add("SNA_Node_IconFromData")
        obj = self.add("SNA_Node_PythonExpression")
        obj.code = "bpy.data.objects['Cube']"
        helpers.flush()
        self.link(obj.outputs["result"], icon.socket("data"))
        self.print_icon(icon.outputs["icon"])
        enum_icon = self.add("SNA_Node_IconFromData")
        enum_icon.source = "ENUM"
        helpers.flush()
        self.link(obj.outputs["result"], enum_icon.socket("data"))
        enum_icon.socket("property").value = "type"
        enum_icon.socket("item").value = "MESH"
        self.print_icon(enum_icon.outputs["icon"])
        cube_icon, mesh_icon = self.run_trigger()
        # what Blender shows (the object's icon differs between versions)
        cube = bpy.data.objects["Cube"]
        self.assertGreater(int(cube_icon), 0)
        self.assertEqual(int(cube_icon), bpy.types.UILayout.icon(cube))
        self.assertEqual(
            int(mesh_icon), bpy.types.UILayout.enum_item_icon(cube, "type", "MESH")
        )

    def print_icon(self, socket):
        """Icons don't convert to text: through an expression."""
        as_number = self.add("SNA_Node_PythonExpression")
        as_number.code = "icon"
        helpers.flush()
        self.link(socket, as_number.socket("name_icon"))
        self.print_value(as_number.outputs["result"])

    def test_addon_info(self):
        bpy.context.scene.sna.addon.version = (2, 3, 4)
        info = self.add("SNA_Node_AddonInfo")
        for key in ("name", "version", "module", "folder"):
            self.print_value(info.outputs[key])
        name, version, module, folder = self.run_trigger()
        self.assertEqual((name, version), ("Value Test", "2.3.4"))
        self.assertEqual(module, bpy.context.scene.sna.addon.module_name)
        self.assertTrue(os.path.isfile(os.path.join(folder, "blender_manifest.toml")))

    # -- flow -------------------------------------------------------------

    def test_repeat_with_break_and_continue(self):
        repeat = self.then("SNA_Node_Repeat")
        repeat.socket("times").value = 6
        branch = self.add("SNA_Node_Switch")
        self.link(repeat.outputs["loop"], branch.inputs[0])
        self.link(repeat.outputs["index"], branch.socket("value"))
        branch.cases[0].value = "1"
        branch.cases[1].value = "4"
        skip = self.add("SNA_Node_LoopControl")
        skip.action = "continue"
        stop = self.add("SNA_Node_LoopControl")
        self.link(branch.outputs["case_0"], skip.inputs[0])
        self.link(branch.outputs["case_1"], stop.inputs[0])
        self.print_value(repeat.outputs["index"], after=branch.outputs["next"])
        done = self.add("SNA_Node_Print")
        done.socket("text").value = "done"
        self.link(repeat.outputs["next"], done.inputs[0])
        self.assertEqual(self.run_trigger(), ["0", "2", "3", "done"])

    def test_switch_default_and_case_rename(self):
        switch = self.then("SNA_Node_Switch")
        self.link(self.string("B"), switch.socket("value"))
        for key, text in (("case_1", "matched"), ("default", "default")):
            printer = self.add("SNA_Node_Print")
            printer.socket("text").value = text
            self.link(switch.outputs[key], printer.inputs[0])
        self.assertEqual(self.run_trigger(), ["matched"])
        switch.cases[1].value = "C"  # rebuilds on its own
        self.assertEqual(switch.outputs["case_1"].name, "C")
        self.assertEqual(self.run_trigger(), ["default"])

    def test_break_outside_a_loop(self):
        node = self.then("SNA_Node_LoopControl")
        helpers.flush()
        self.assertIsNotNone(errors().addon_error)
        self.assertIn("outside loop", errors().node_message(node.id) or "")

    def test_redraw(self):
        redraw = self.then("SNA_Node_Redraw")
        redraw.area_type = "VIEW_3D"
        self.assertIn("sn_redraw('VIEW_3D')", self.source())
        self.run_trigger()
