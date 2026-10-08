"""Functions (node groups): the tree interface, the compiled function and
the Group node calling it."""

import sys
import unittest

import bpy
import helpers

FLOW = "ScriptingFlowSocket"
FLOAT = "ScriptingFloatSocket"
STRING = "ScriptingStringSocket"
INTEGER = "ScriptingIntegerSocket"


def errors():
    return helpers.sn("src.core.errors")


def generated(tree):
    """The generated function of a function tree."""
    module = next(
        m for name, m in sys.modules.items() if name.endswith("." + tree.module_name)
    )
    return getattr(module, tree.module_name)


def item(tree, name):
    return next(i for i in tree.interface.items_tree if i.name == name)


class GroupsTest(unittest.TestCase):
    def setUp(self):
        helpers.reset_file()
        bpy.context.scene.sna.addon.addon_name = "Group Test"

    def tearDown(self):
        for tree in list(bpy.data.node_groups):
            bpy.data.node_groups.remove(tree)
        helpers.sn("src.core.scheduler").request_full()
        helpers.flush()

    def assertLoaded(self):
        self.assertIsNone(errors().addon_error)

    def double(self):
        """Double(Value) -> Result: a pure function."""
        function, group_input, group_output = helpers.new_function(
            "Double", inputs=[("Value", FLOAT)], outputs=[("Result", FLOAT)]
        )
        math = helpers.add_node(function, "SNA_Node_Math")
        math.operation = "MULTIPLY"
        math.inputs["b"].value = 2
        helpers.link(function, group_input.outputs[0], math.inputs["a"])
        helpers.link(function, math.outputs["result"], group_output.inputs[0])
        helpers.flush()
        return function

    def greet(self):
        """Greet(Run, Name) -> (Next, Greeting): prints and returns the name."""
        function, group_input, group_output = helpers.new_function(
            "Greet",
            inputs=[("Run", FLOW), ("Name", STRING)],
            outputs=[("Next", FLOW), ("Greeting", STRING)],
        )
        p = helpers.add_node(function, "SNA_Node_Print")
        helpers.link(function, group_input.outputs[0], p.inputs[0])
        helpers.link(function, group_input.outputs[1], p.inputs["text"])
        helpers.link(function, p.outputs[0], group_output.inputs[0])
        helpers.link(function, group_input.outputs[1], group_output.inputs[1])
        helpers.flush()
        return function

    # -- the function -------------------------------------------------------

    def test_pure_function(self):
        function = self.double()
        source = helpers.tree_source(function)
        self.assertIn(
            f"def {function.module_name}(value, *, self=None, context=None, "
            "layout=None, event=None):",
            source,
        )
        self.assertIn("return (value * 2.0)", source)
        self.assertLoaded()
        self.assertEqual(generated(function)(21.0), 42.0)

    def test_flow_function_returns_where_the_flow_ends(self):
        function = self.greet()
        source = helpers.tree_source(function)
        self.assertIn(f"def {function.module_name}(name, *,", source)
        self.assertIn("return name", source)
        self.assertLoaded()
        self.assertEqual(generated(function)("Bob"), "Bob")

    def test_return_inside_a_branch(self):
        function, group_input, group_output = helpers.new_function(
            "Check",
            inputs=[("Run", FLOW), ("Flag", "ScriptingBooleanSocket")],
            outputs=[("Next", FLOW), ("Result", STRING)],
        )
        group_output.inputs[1].value = "no"
        branch = helpers.add_node(function, "SNA_Node_IfElse")
        helpers.link(function, group_input.outputs[0], branch.inputs[0])
        helpers.link(function, group_input.outputs[1], branch.inputs["condition"])
        helpers.link(function, branch.outputs["then"], group_output.inputs[0])
        helpers.flush()
        source = helpers.tree_source(function)
        self.assertIn("if flag:\n        return 'no'", source)
        self.assertLoaded()
        self.assertEqual(generated(function)(True), "no")
        self.assertIsNone(generated(function)(False))

    def test_parameter_names_are_unique_identifiers(self):
        function, _, _ = helpers.new_function(
            "Names",
            inputs=[("My Value", FLOAT), ("my value", FLOAT), ("self", FLOAT)],
        )
        params = helpers.sn("src.core.functions").parameters(function)
        self.assertEqual(
            [name for _, name in params], ["my_value", "my_value_2", "self_2"]
        )

    # -- calling it ---------------------------------------------------------

    def test_pure_function_call_is_an_expression(self):
        function = self.double()
        tree = helpers.new_tree("Main")
        trigger = helpers.add_node(tree, "SNA_Node_Trigger")
        call = helpers.call_function(tree, function)
        self.assertEqual([s.name for s in call.inputs], ["Value"])
        self.assertEqual([s.name for s in call.outputs], ["Result"])
        call.inputs[0].value = 4
        p = helpers.add_node(tree, "SNA_Node_Print")
        helpers.link(tree, trigger.outputs[0], p.inputs[0])
        helpers.link(tree, call.outputs[0], p.inputs["text"])
        helpers.flush()
        source = helpers.tree_source(tree)
        name = function.module_name
        self.assertIn(f"from .{name} import {name}", source)
        self.assertIn(f"{name}(4.0, self=self, context=context)", source)
        self.assertLoaded()

    def test_flow_call_continues_after_the_call(self):
        function = self.greet()
        tree = helpers.new_tree("Main")
        trigger = helpers.add_node(tree, "SNA_Node_Trigger")
        call = helpers.call_function(tree, function)
        self.assertEqual([s.name for s in call.inputs], ["Run", "Name"])
        self.assertEqual([s.name for s in call.outputs], ["Next", "Greeting"])
        call.inputs[1].value = "Ann"
        p = helpers.add_node(tree, "SNA_Node_Print")
        helpers.link(tree, trigger.outputs[0], call.inputs[0])
        helpers.link(tree, call.outputs[0], p.inputs[0])
        helpers.link(tree, call.outputs[1], p.inputs["text"])
        helpers.flush()
        source = helpers.tree_source(tree)
        self.assertRegex(
            source, rf"(result_\d+) = {function.module_name}\('Ann'.*\n.*\1"
        )
        self.assertLoaded()
        namespace, op = trigger.operator_idname.split(".")
        self.assertEqual(getattr(getattr(bpy.ops, namespace), op)(), {"FINISHED"})

    def test_interface_function_gets_the_layout(self):
        function, group_input, group_output = helpers.new_function(
            "Header", inputs=[("Layout", FLOW)], outputs=[("Next", FLOW)]
        )
        item(function, "Layout").kind = "INTERFACE"
        item(function, "Next").kind = "INTERFACE"
        helpers.flush()
        label = helpers.add_node(function, "SNA_Node_Label")
        label.inputs["text"].value = "From a function"
        helpers.link(function, group_input.outputs[0], label.inputs[0])
        helpers.link(function, label.outputs[0], group_output.inputs[0])

        tree = helpers.new_tree("Main")
        panel = helpers.add_node(tree, "SNA_Node_Panel")
        call = helpers.call_function(tree, function)
        self.assertEqual(call.inputs[0].kind, "INTERFACE")
        helpers.link(tree, panel.outputs["body"], call.inputs[0])
        helpers.flush()
        self.assertIn(
            "layout.label(text='From a function')", helpers.tree_source(function)
        )
        self.assertIn("layout=self.layout)", helpers.tree_source(tree))
        self.assertNotIn("return", helpers.tree_source(function))
        self.assertLoaded()

    def test_links_survive_rename_reorder_and_new_items(self):
        function = self.double()
        function.interface.new_socket("Offset", in_out="INPUT", socket_type=FLOAT)
        tree = helpers.new_tree("Main")
        call = helpers.call_function(tree, function)
        number = helpers.add_node(tree, "SNA_Node_Float")
        helpers.link(tree, number.outputs[0], call.inputs["Value"])
        helpers.flush()

        value = item(function, "Value")
        value.name = "Amount"
        function.interface.move(value, len(function.interface.items_tree))
        function.interface.new_socket("Extra", in_out="INPUT", socket_type=FLOAT)
        function.update()
        helpers.flush()
        self.assertEqual([s.name for s in call.inputs], ["Offset", "Amount", "Extra"])
        self.assertTrue(call.inputs["Amount"].is_linked)
        self.assertEqual(call.inputs["Amount"].identifier, value.identifier)
        self.assertLoaded()

    def test_default_values_come_from_the_interface(self):
        function, _, _ = helpers.new_function("Defaults")
        count = function.interface.new_socket(
            "Count", in_out="INPUT", socket_type=INTEGER
        )
        count.default_value = 7
        tree = helpers.new_tree("Main")
        call = helpers.call_function(tree, function)
        self.assertEqual(call.inputs[0].value, 7)

    def test_linking_the_empty_socket_adds_an_item(self):
        function, _, group_output = helpers.new_function("Extend")
        number = helpers.add_node(function, "SNA_Node_Integer")
        function.links.new(
            number.outputs[0], group_output.inputs[-1], handle_dynamic_sockets=True
        )
        new = function.interface.items_tree[0]
        self.assertEqual(new.bl_socket_idname, INTEGER)
        self.assertEqual(new.in_out, "OUTPUT")

    def test_interface_problems_show_on_the_call(self):
        function, _, _ = helpers.new_function(
            "Two Flows", inputs=[("A", FLOW), ("B", FLOW)]
        )
        tree = helpers.new_tree("Main")
        trigger = helpers.add_node(tree, "SNA_Node_Trigger")
        call = helpers.call_function(tree, function)
        helpers.link(tree, trigger.outputs[0], call.inputs[0])
        helpers.flush()
        self.assertIn("more than one flow input", errors().node_message(call.id))

    def test_functions_cant_call_themselves(self):
        outer = self.double()
        inner, _, _ = helpers.new_function("Inner", inputs=[("X", FLOAT)])
        helpers.call_function(outer, inner)
        call = helpers.add_node(inner, "SNA_Node_Group")
        poll = type(call).poll_instance
        self.assertFalse(poll(call, inner))  # itself
        self.assertFalse(poll(call, outer))  # calls this one
        self.assertTrue(poll(call, self.greet()))

    def test_trees_without_interface_are_not_functions(self):
        tree = helpers.new_tree("Main")
        self.assertFalse(tree.is_function)
        self.assertTrue(self.double().is_function)
        self.assertNotIn("def main_", helpers.tree_source(tree))


if __name__ == "__main__":
    unittest.main()
