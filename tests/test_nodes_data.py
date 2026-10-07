"""Generated code of the data, list and math nodes."""

import re
import unittest

import bpy
import helpers


def node_errors():
    return helpers.sn("src.core.errors").node_errors


class DataNodesTest(unittest.TestCase):
    def setUp(self):
        helpers.reset_file()
        bpy.context.scene.sna.addon.addon_name = "Data Test"
        self.tree = helpers.new_tree()
        self.trigger = helpers.add_node(self.tree, "SNA_Node_Trigger")

    def tearDown(self):
        for tree in list(bpy.data.node_groups):
            bpy.data.node_groups.remove(tree)
        helpers.sn("src.core.scheduler").request_full()
        helpers.flush()

    def add(self, idname):
        return helpers.add_node(self.tree, idname)

    def link(self, from_socket, to_socket):
        helpers.link(self.tree, from_socket, to_socket)

    def print_value(self, socket, after=None):
        """A Print node in the flow after `after` (the trigger) printing `socket`."""
        p = self.add("SNA_Node_Print")
        self.link(after or self.trigger.outputs[0], p.inputs[0])
        self.link(socket, p.inputs["text"])
        return p

    def source(self):
        helpers.flush()
        self.assertIsNone(helpers.sn("src.core.errors").addon_error)
        # unformatted, so expressions aren't wrapped over several lines
        compiler = helpers.sn("src.core.compiler")
        source = compiler.compile_tree(self.tree, pretty=False)
        compile(source, "<tree>", "exec")
        return source

    def run_trigger(self):
        namespace, op = self.trigger.operator_idname.split(".")
        return getattr(getattr(bpy.ops, namespace), op)()

    # -- values ---------------------------------------------------------------

    def test_value_node_is_converted(self):
        number = self.add("SNA_Node_Integer")
        number.value = 42
        self.print_value(number.outputs["value"])
        self.assertIn("str(42)", self.source())

    def test_string_value_is_escaped(self):
        string = self.add("SNA_Node_String")
        string.value = 'it\'s "quoted"\n'
        self.print_value(string.outputs["value"])
        self.assertIn(repr(string.value), self.source())

    def test_compare(self):
        compare = self.add("SNA_Node_Compare")
        compare.comparison_type = ">="
        a, b = self.add("SNA_Node_Integer"), self.add("SNA_Node_Float")
        a.value, b.value = 3, 2.5
        self.link(a.outputs["value"], compare.inputs["a"])
        self.link(b.outputs["value"], compare.inputs["b"])
        self.print_value(compare.outputs["result"])
        self.assertIn("str((3 >= 2.5))", self.source())

    def test_vector_math(self):
        math = self.add("SNA_Node_VectorMath")
        math.operation = "DOT"
        self.assertEqual(math.outputs["result"].bl_idname, "ScriptingFloatSocket")
        math.operation = "NORMALIZE"
        self.assertFalse(math.socket("b").enabled)
        self.assertEqual(math.outputs["result"].bl_idname, "ScriptingVectorSocket")
        math.operation = "CROSS"
        math.dimension = "2"  # the cross product is always 3D
        self.assertEqual(math.inputs["a"].dimension, "3")
        math.inputs["a"].value = (1, 0, 0, 0)
        math.inputs["b"].value = (0, 1, 0, 0)
        self.print_value(math.outputs["result"])
        source = self.source()
        self.assertIn("(1.0, 0.0, 0.0)[1] * (0.0, 1.0, 0.0)[2]", source)
        math.operation = "DISTANCE"
        self.assertIn("import math", self.source())

    def test_switch_data_types_all_sockets(self):
        switch = self.add("SNA_Node_SwitchData")
        switch.data_type = "ScriptingIntegerSocket"
        for key in ("true", "false"):
            self.assertEqual(switch.inputs[key].bl_idname, "ScriptingIntegerSocket")
        self.assertEqual(switch.outputs["result"].bl_idname, "ScriptingIntegerSocket")
        switch.inputs["true"].value = 1
        switch.inputs["false"].value = 2
        self.print_value(switch.outputs["result"])
        self.assertIn("(1 if False else 2)", self.source())

    # -- lists ------------------------------------------------------------------

    def test_create_list_dynamic_inputs(self):
        create = self.add("SNA_Node_CreateList")
        for text in ("a", "b"):
            string = self.add("SNA_Node_String")
            string.value = text
            self.link(string.outputs["value"], create.inputs[-1])
        self.assertEqual(len(create.inputs), 3)  # two items and the "+" socket
        self.print_value(create.outputs["list"])
        self.assertIn("str(['a', 'b'])", self.source())

    def test_list_slice_end_zero_means_none(self):
        slice_node = self.add("SNA_Node_ListSlice")
        slice_node.inputs["start"].value = 1
        self.print_value(slice_node.outputs["slice"])
        self.assertIn("[][1:None]", self.source())
        slice_node.inputs["end"].value = 2
        self.assertIn("[][1:2]", self.source())

    def test_for_each_item_is_scoped_to_the_loop(self):
        create = self.add("SNA_Node_CreateList")
        string = self.add("SNA_Node_String")
        string.value = "x"
        self.link(string.outputs["value"], create.inputs[-1])
        loop = self.add("SNA_Node_ForEachList")
        self.link(self.trigger.outputs[0], loop.inputs[0])
        self.link(create.outputs["list"], loop.inputs["list"])
        inside = self.print_value(loop.outputs["item"], after=loop.outputs["loop"])
        index = self.print_value(loop.outputs["index"], after=inside.outputs[0])
        outside = self.print_value(loop.outputs["item"], after=loop.outputs["next"])
        source = self.source()

        match = re.search(r"( *)for (index_\d+), (item_\d+) in enumerate\(", source)
        self.assertIsNotNone(match, source)
        indent, index_var, item_var = match.groups()
        body = indent + "    "
        self.assertRegex(source, rf"\n{body}\w+\(str\({item_var}\)\)")
        self.assertRegex(source, rf"\n{body}\w+\(str\({index_var}\)\)")
        # outside of the loop the item doesn't exist: error on that node
        self.assertIn("isn't available here", node_errors().get(outside.id, ""))
        self.assertNotIn(inside.id, node_errors())
        self.assertNotIn(index.id, node_errors())
        self.assertEqual(self.run_trigger(), {"FINISHED"})

    def test_list_pop_output_follows_the_flow(self):
        create = self.add("SNA_Node_CreateList")
        for value in (1, 2):
            number = self.add("SNA_Node_Integer")
            number.value = value
            self.link(number.outputs["value"], create.inputs[-1])
        pop = self.add("SNA_Node_ListPop")
        self.link(self.trigger.outputs[0], pop.inputs[0])
        self.link(create.outputs["list"], pop.inputs["list"])
        self.print_value(pop.outputs["item"], after=pop.outputs["next"])
        source = self.source()
        self.assertRegex(
            source, r"popped_\d+ = \[1, 2\]\.pop\(-1\) if \[1, 2\] else None"
        )
        self.assertEqual(self.run_trigger(), {"FINISHED"})


if __name__ == "__main__":
    unittest.main()
