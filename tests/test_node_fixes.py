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

    def test_blend_data_key_mode_updates_sockets(self):
        tree = helpers.new_tree()
        node = helpers.add_node(tree, "SNA_Node_BlendData")
        node.path_root = "DATA"
        node.path = "objects[]"
        self.assertEqual(node.socket("key_0").bl_idname, "ScriptingIntegerSocket")
        node.path_keys[0].mode = "NAME"
        self.assertEqual(node.socket("key_0").bl_idname, "ScriptingStringSocket")
        node.socket("key_0").value = "Cube"
        trigger = helpers.add_node(tree, "SNA_Node_Trigger")
        p = helpers.add_node(tree, "SNA_Node_Print")
        helpers.link(tree, trigger.outputs[0], p.inputs[0])
        helpers.link(tree, node.outputs[0], p.inputs[1])
        helpers.flush()
        self.assertIn("bpy.data.objects['Cube']", helpers.tree_source(tree))
