"""String nodes, Report, timers (Run with Delay / in Intervals), Add to
Menu / Panel / Header and Shortcut: generated code, run where Blender allows
it in background mode (keymaps: tests/gui/shortcuts.py)."""

import contextlib
import importlib
import io
import sys
import unittest

import bpy
import helpers


def errors():
    return helpers.sn("src.core.errors")


def generated_helpers():
    package = sys.modules[bpy.context.scene.sna.addon.module_name]
    return importlib.import_module(package.__name__ + "._sn_helpers")


class UtilityNodesTest(unittest.TestCase):
    def setUp(self):
        helpers.reset_file()
        bpy.context.scene.sna.addon.addon_name = "Utility Test"
        self.tree = helpers.new_tree("Main")
        self.trigger = helpers.add_node(self.tree, "SNA_Node_Trigger")
        self.last = self.trigger.outputs[0]

    def tearDown(self):
        for tree in list(bpy.data.node_groups):
            bpy.data.node_groups.remove(tree)
        helpers.sn("src.core.scheduler").request_full()
        helpers.flush()

    def add(self, idname):
        return helpers.add_node(self.tree, idname)

    def link(self, from_socket, to_socket):
        helpers.link(self.tree, from_socket, to_socket)

    def then(self, idname):
        """A flow node after the last one."""
        node = self.add(idname)
        self.link(self.last, node.inputs[0])
        self.last = next(s for s in node.outputs if s.identifier == "next")
        return node

    def print_value(self, socket):
        printer = self.then("SNA_Node_Print")
        self.link(socket, printer.inputs["text"])

    def run_trigger(self):
        """Run the trigger, return what it printed (one line per print)."""
        helpers.flush()
        self.assertIsNone(errors().addon_error)
        self.assertEqual(dict(errors().node_errors), {})
        namespace, op = self.trigger.operator_idname.split(".")
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            getattr(getattr(bpy.ops, namespace), op)()
        return out.getvalue().splitlines()

    def string(self, text):
        node = self.add("SNA_Node_String")
        node.value = text
        return node.outputs["value"]

    # -- strings ------------------------------------------------------------

    def string_node(self, idname, **values):
        node = self.add(idname)
        for key, value in values.items():
            socket = node.socket(key)
            if isinstance(value, str) and socket.bl_idname.endswith("StringSocket"):
                self.link(self.string(value), socket)
            else:
                socket.value = value
        return node

    def test_string_nodes(self):
        cases = [
            ("SNA_Node_SplitString", {"string": "a b  c"}, "list", "['a', 'b', 'c']"),
            ("SNA_Node_SplitString", {"string": "a,b,c", "separator": ",", "max_splits": 1}, "list", "['a', 'b,c']"),
            ("SNA_Node_ReplaceString", {"string": "a-b-c", "find": "-", "replace": "+"}, "string", "a+b+c"),
            ("SNA_Node_SliceString", {"string": "abcdef", "start": 1, "length": 3}, "string", "bcd"),
            ("SNA_Node_SliceString", {"string": "abcdef", "start": -2}, "string", "ef"),
            ("SNA_Node_SliceString", {"string": "abcdef", "start": -3, "length": 3}, "string", "def"),
            ("SNA_Node_StringLength", {"string": "abcd"}, "length", "4"),
            ("SNA_Node_TrimString", {"string": "  ab \n"}, "string", "ab"),
            ("SNA_Node_TrimString", {"string": "xxabxx", "characters": "x"}, "string", "ab"),
            ("SNA_Node_PadString", {"string": "7", "length": 3}, "string", "007"),
            ("SNA_Node_FindInString", {"string": "banana", "find": "an"}, "index", "1"),
            ("SNA_Node_FindInString", {"string": "banana", "find": "an"}, "count", "2"),
        ]  # fmt: skip
        for idname, values, output, expected in cases:
            with self.subTest(node=idname, values=values):
                self.setUp()
                node = self.string_node(idname, **values)
                self.print_value(node.outputs[output])
                self.assertEqual(self.run_trigger(), [expected])

    def test_string_modes(self):
        case = self.string_node("SNA_Node_ChangeCase", string="hello world")
        case.case = "title"
        trim = self.string_node("SNA_Node_TrimString", string="..ab..", characters=".")
        trim.side = "rstrip"
        pad = self.string_node("SNA_Node_PadString", string="ab", length=4, fill="*-")
        pad.alignment = "ljust"
        substring = self.string_node("SNA_Node_Substring", string="Cube.001")
        substring.mode = "STARTS"
        substring.case_sensitive = False
        self.link(self.string("cube"), substring.socket("substring"))
        for node in (case, trim, pad, substring):
            self.print_value(node.outputs[0])
        self.assertEqual(self.run_trigger(), ["Hello World", "..ab", "ab**", "True"])

    def test_join_and_format(self):
        split = self.string_node("SNA_Node_SplitString", string="a b c")
        join = self.add("SNA_Node_JoinList")
        self.link(split.outputs["list"], join.socket("list"))
        self.print_value(join.outputs["string"])
        format_ = self.add("SNA_Node_FormatString")
        format_.socket("format").value = "{} has {:.1f}"
        number = self.add("SNA_Node_Float")
        number.value = 2.25
        self.link(self.string("Cube"), format_.inputs[-1])
        self.link(number.outputs["value"], format_.inputs[-1])
        self.print_value(format_.outputs["string"])
        self.assertEqual(self.run_trigger(), ["a, b, c", "Cube has 2.2"])

    # -- report -------------------------------------------------------------

    def test_report_outside_an_operator_prints(self):
        report = self.then("SNA_Node_Report")
        report.kind = "WARNING"
        report.socket("message").value = "Careful"
        self.assertEqual(self.run_trigger(), ["Warning: Careful"])

    def test_report_in_an_operator(self):
        operator = self.add("SNA_Node_Operator")
        report = self.add("SNA_Node_Report")
        report.socket("message").value = "Done"
        self.link(operator.outputs["execute"], report.inputs[0])
        helpers.flush()
        self.assertIn("sn_report(self, 'INFO', 'Done')", helpers.tree_source(self.tree))
        namespace, op = operator.operator_idname.split(".")
        self.assertEqual(getattr(getattr(bpy.ops, namespace), op)(), {"FINISHED"})

    def test_report_in_exported_addon(self):
        self.then("SNA_Node_Report")
        helpers.flush()
        files = helpers.sn("src.core.compiler").compile_addon(dev=False)
        self.assertIn("print(f", files["_sn_helpers.py"])
        self.assertNotIn("sn_print", files["_sn_helpers.py"])

    # -- timers -------------------------------------------------------------

    def test_run_with_delay(self):
        delay = self.then("SNA_Node_RunWithDelay")
        delay.socket("delay").value = 0.5
        printer = self.add("SNA_Node_Print")
        printer.socket("text").value = "later"
        self.link(delay.outputs["delayed"], printer.inputs[0])
        self.assertEqual(self.run_trigger(), [])  # not yet
        timers = generated_helpers()._sn_timers
        self.assertEqual(len(timers), 1)
        timer = timers[0]
        self.assertTrue(bpy.app.timers.is_registered(timer))
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            timer()  # what Blender does after half a second
        self.assertEqual(out.getvalue().splitlines(), ["later"])
        self.assertEqual(timers, [])

    def test_run_in_intervals(self):
        intervals = self.then("SNA_Node_RunInIntervals")
        intervals.socket("interval").value = 0.25
        intervals.socket("times").value = 3
        self.print_value_in(intervals, "repeat", intervals.outputs["index"])
        self.run_trigger()
        timers = generated_helpers()._sn_timers
        timer = timers[0]
        out = io.StringIO()
        with contextlib.redirect_stdout(out):
            results = [timer() for _ in range(3)]
        self.assertEqual(out.getvalue().splitlines(), ["0", "1", "2"])
        self.assertEqual(results, [0.25, 0.25, None])
        self.assertEqual(timers, [])

    def test_keep_running_stops_intervals(self):
        intervals = self.then("SNA_Node_RunInIntervals")
        intervals.socket("keep_running").value = False
        self.run_trigger()
        timer = generated_helpers()._sn_timers[0]
        self.assertIsNone(timer())

    def test_timers_stop_on_rebuild(self):
        self.then("SNA_Node_RunWithDelay")
        self.run_trigger()
        timer = generated_helpers()._sn_timers[0]
        self.assertTrue(bpy.app.timers.is_registered(timer))
        bpy.context.scene.sna.addon.addon_name = "Utility Test 2"  # reloads
        helpers.flush()
        self.assertFalse(bpy.app.timers.is_registered(timer))

    def print_value_in(self, node, flow, socket):
        printer = self.add("SNA_Node_Print")
        self.link(node.outputs[flow], printer.inputs[0])
        self.link(socket, printer.inputs["text"])

    # -- add to menu / panel / header -------------------------------------

    def test_add_to_menu(self):
        node = self.add("SNA_Node_AddToMenu")
        node.target = "Object  [VIEW3D_MT_object]"
        node.position = "prepend"
        label = self.add("SNA_Node_Label")
        label.socket("text").value = "Hello"
        self.link(node.outputs[0], label.inputs[0])
        helpers.flush()
        self.assertIsNone(errors().addon_error)
        source = helpers.tree_source(self.tree)
        self.assertIn("def draw_object_menu(self, context):", source)
        self.assertIn("bpy.types.VIEW3D_MT_object.prepend(draw_object_menu)", source)
        draw_funcs = bpy.types.VIEW3D_MT_object._dyn_ui_initialize()
        self.assertIn("draw_object_menu", [f.__name__ for f in draw_funcs])
        self.tree.nodes.remove(node)
        helpers.flush()
        draw_funcs = bpy.types.VIEW3D_MT_object._dyn_ui_initialize()
        self.assertNotIn("draw_object_menu", [f.__name__ for f in draw_funcs])

    def test_add_to_targets(self):
        cases = [
            ("SNA_Node_AddToPanel", "VIEW3D_PT_context_properties", True),
            ("SNA_Node_AddToHeader", "VIEW3D_HT_header", True),
            ("SNA_Node_AddToMenu", "VIEW3D_PT_context_properties", False),  # a panel
            ("SNA_Node_AddToMenu", "NOT_A_MENU", False),
        ]
        for idname, target, valid in cases:
            with self.subTest(node=idname, target=target):
                self.setUp()
                node = self.add(idname)
                node.target = target
                helpers.flush()
                message = errors().node_message(node.id)
                if valid:
                    self.assertIsNone(message)
                    self.assertIn(
                        f"bpy.types.{target}.append", helpers.tree_source(self.tree)
                    )
                else:
                    self.assertIn(
                        "NOT_A_MENU" if "NOT" in target else "No menu", message
                    )

    def test_add_to_search_lists_blender_classes(self):
        add_to = helpers.sn("src.nodes.categories.interface.node_add_to")
        menus = dict(
            (name, display) for display, name in add_to.classes(bpy.types.Menu)
        )
        self.assertEqual(menus["VIEW3D_MT_object"], "Object  [VIEW3D_MT_object]")
        self.assertFalse(any(name.startswith("SNA_") for name in menus))
        self.assertEqual(
            add_to.class_name("Object  [VIEW3D_MT_object]"), "VIEW3D_MT_object"
        )

    def test_hidden_add_to_draws_nothing(self):
        node = self.add("SNA_Node_AddToPanel")
        node.target = "VIEW3D_PT_context_properties"
        node.socket("visible").value = False
        helpers.flush()
        self.assertIn("if not False:\n        return", helpers.tree_source(self.tree))

    # -- shortcuts ----------------------------------------------------------

    def test_shortcut_runs_operator(self):
        operator = self.add("SNA_Node_Operator")
        operator.socket("label").value = "Greet"
        shortcut = self.add("SNA_Node_Shortcut")
        helpers.point(shortcut, "operator_sn", operator)
        shortcut.key = "G"
        shortcut.ctrl = shortcut.shift = True
        shortcut.keymap = "3D View"
        helpers.flush()
        self.assertIsNone(errors().node_message(shortcut.id))
        source = helpers.tree_source(self.tree)
        self.assertIn(
            "sn_add_shortcut('3D View', 'VIEW_3D', 'utility_test.greet', 'G', ctrl=True, shift=True)",
            source,
        )
        shortcut_mod = helpers.sn("src.nodes.categories.logic.node_shortcut")
        self.assertEqual(shortcut_mod.key_text(shortcut), "Ctrl Shift G")

    def test_shortcut_with_properties_and_value(self):
        shortcut = self.add("SNA_Node_Shortcut")
        shortcut.mode = "BLENDER"
        shortcut.operator_blender = "mesh.primitive_cube_add"
        shortcut.value = "DOUBLE_CLICK"
        helpers.flush()
        shortcut.socket("arg_size").value = 3.0
        helpers.flush()
        self.assertIn(
            "'mesh.primitive_cube_add', 'A', 'DOUBLE_CLICK', properties={'size': 3.0})",
            helpers.tree_source(self.tree),
        )
        self.assertIsNone(errors().addon_error)  # no keyconfig in background

    def test_shortcut_opens_menu(self):
        panel = self.add("SNA_Node_Panel")
        menu = self.add("SNA_Node_Menu")
        menu.socket("label").value = "Tools"
        self.link(panel.outputs["body"], menu.inputs[0])
        shortcut = self.add("SNA_Node_Shortcut")
        shortcut.action = "MENU"
        helpers.flush()
        self.assertEqual(errors().node_message(shortcut.id), "Pick a menu")
        helpers.point(shortcut, "menu", menu)
        helpers.flush()
        self.assertIn(
            "'wm.call_menu', 'A', properties={'name': 'UTILITY_TEST_MT_tools'})",
            helpers.tree_source(self.tree),
        )

    def test_shortcut_needs_a_known_keymap(self):
        shortcut = self.add("SNA_Node_Shortcut")
        shortcut.mode = "BLENDER"
        shortcut.operator_blender = "wm.save_mainfile"
        shortcut.keymap = "Nowhere"
        helpers.flush()
        self.assertIn("Unknown place", errors().node_message(shortcut.id))
        keymaps = helpers.sn("src.nodes.categories.logic.node_shortcut").keymaps()
        self.assertEqual(keymaps["Object Mode"], "EMPTY")
        self.assertEqual(keymaps["Node Editor"], "NODE_EDITOR")
        self.assertFalse(any("Modal" in name for name in keymaps))


if __name__ == "__main__":
    unittest.main()
