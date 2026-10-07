"""Regression tests for node/socket level bugs found in the audit."""

import unittest

import bpy
import helpers


def errors():
    return helpers.sn("src.core.errors")


class NodeFixesTest(unittest.TestCase):
    def setUp(self):
        helpers.reset_file()
        bpy.context.scene.sna.addon.addon_name = "Fix Test"

    def tearDown(self):
        for tree in list(bpy.data.node_groups):
            bpy.data.node_groups.remove(tree)
        helpers.sn("src.core.scheduler").request_full()
        helpers.flush()

    def test_user_text_is_escaped(self):
        tree = helpers.new_tree()
        trigger = helpers.add_node(tree, "SNA_Node_Trigger")
        p = helpers.add_node(tree, "SNA_Node_Print")
        nasty = "He said \"hi\" \\ and 'bye'\n"
        p.inputs[1].value = nasty
        helpers.link(tree, trigger.outputs[0], p.inputs[0])
        helpers.flush()
        source = helpers.tree_source(tree)
        compile(source, "<tree>", "exec")
        self.assertIn(repr(nasty), source)

    def test_boolean_math_uses_both_inputs(self):
        tree = helpers.new_tree()
        trigger = helpers.add_node(tree, "SNA_Node_Trigger")
        p = helpers.add_node(tree, "SNA_Node_Print")
        node = helpers.add_node(tree, "SNA_BooleanMath")
        node.comparison = "OR"
        node.inputs[0].value = True
        node.inputs[1].value = False
        helpers.link(tree, trigger.outputs[0], p.inputs[0])
        helpers.link(tree, node.outputs[0], p.inputs[1])
        helpers.flush()
        # Boolean -> String conversion wraps the value: str((True or False))
        self.assertIn("(True or False)", helpers.tree_source(tree))

    def test_precedence_is_kept(self):
        code_format = helpers.sn("src.lib.code_format")
        self.assertEqual(code_format.parenthesize("a + b"), "(a + b)")
        self.assertEqual(code_format.parenthesize("foo(a + b)"), "foo(a + b)")
        self.assertEqual(code_format.parenthesize("x.y[0]"), "x.y[0]")
        self.assertEqual(code_format.parenthesize("1, 2"), "(1, 2)")

    def test_conversion_evaluates_source_once(self):
        conversions = helpers.sn("src.sockets.conversions")
        code = conversions.get_conversion(
            "ScriptingFloatSocket", "ScriptingVectorSocket", "next(counter)"
        )
        self.assertEqual(code.count("next(counter)"), 1)
        counter = iter(range(10))
        self.assertEqual(eval(code, {"counter": counter}), (0, 0, 0))

    def test_flow_outputs_take_one_link(self):
        tree = helpers.new_tree()
        trigger = helpers.add_node(tree, "SNA_Node_Trigger")
        self.assertEqual(trigger.outputs[0].link_limit, 1)

    def test_blend_data_access_mode_updates_sockets(self):
        tree = helpers.new_tree()
        node = helpers.add_node(tree, "SNA_Node_BlendData")
        node.setup_from_path("bpy.data.objects", is_root=True)
        node.access_mode = "INDEX"
        self.assertIn("Index", node.inputs)
        node.access_mode = "NAME"
        self.assertIn("Name", node.inputs)
        self.assertNotIn("Index", node.inputs)
        helpers.flush()
        self.assertIn("[", node.outputs[0].code)

    # -- script node ------------------------------------------------------------

    def _script_tree(self, text_body):
        tree = helpers.new_tree()
        trigger = helpers.add_node(tree, "SNA_Node_Trigger")
        script = helpers.add_node(tree, "SNA_Node_Script")
        text = bpy.data.texts.new("script.py")
        text.write(text_body)
        script.text_block = text
        helpers.link(tree, trigger.outputs[0], script.inputs[0])
        helpers.flush()
        return tree, trigger, script, text

    def test_script_text_edits_regenerate(self):
        tree, _, script, text = self._script_tree("x = 1\n")
        scheduler = helpers.sn("src.core.scheduler")
        scheduler._run_watchers()  # records the current source
        text.clear()
        text.write("x = 2\n")
        scheduler._run_watchers()
        helpers.flush()
        self.assertIn("x = 2", helpers.tree_source(tree))

    def test_script_keeps_blank_lines_in_strings(self):
        body = 's = """a\n\nb"""\nprint(s)\n'
        tree, _, script, _ = self._script_tree(body)
        # same value, written as a single-line literal so indenting is safe
        self.assertIn(repr("a\n\nb"), helpers.tree_source(tree))

    def test_script_variable_changes_keep_links(self):
        tree, _, script, _ = self._script_tree("pass\n")
        script.add_variable("value", "ScriptingStringSocket", False)
        string = helpers.add_node(tree, "SNA_Node_String")
        helpers.link(tree, string.outputs[0], script.inputs["value"])
        script.add_variable("other", "ScriptingStringSocket", False)
        self.assertTrue(script.inputs["value"].is_linked)

    def test_load_error_is_shown_on_the_script_node(self):
        tree, trigger, script, text = self._script_tree("print('ok')\n")
        text.clear()
        text.write("def broken(:\n    pass\n")
        script._generate()
        helpers.flush()
        self.assertIn("syntax error", errors().addon_error)
        self.assertIn(script.id, errors().load_errors)
        self.assertNotIn(trigger.id, errors().load_errors)
        # fixing it clears the error
        text.clear()
        text.write("print('fixed')\n")
        script._generate()
        helpers.flush()
        self.assertIsNone(errors().addon_error)
        self.assertEqual(errors().load_errors, {})
