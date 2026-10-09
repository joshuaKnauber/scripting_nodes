"""Readable names in the generated add-on (core/naming.py)."""

import unittest

import bpy
import helpers

FLOAT = "ScriptingFloatSocket"


def errors():
    return helpers.sn("src.core.errors")


class NamingTest(unittest.TestCase):
    def setUp(self):
        helpers.reset_file()
        bpy.context.scene.sna.addon.addon_name = "Mesh Helper"

    def tearDown(self):
        for tree in list(bpy.data.node_groups):
            bpy.data.node_groups.remove(tree)
        helpers.sn("src.core.scheduler").request_full()
        helpers.flush()

    def operator(self, tree, label, location=(0, 0)):
        node = helpers.add_node(tree, "SNA_Node_Operator", location)
        node.inputs["label"].value = label
        return node

    def test_names_come_from_labels(self):
        tree = helpers.new_tree("Main")
        op = self.operator(tree, "Duplicate Copies")
        helpers.flush()
        source = helpers.tree_source(tree)
        self.assertEqual(tree.module_name, "main")
        self.assertEqual(op.operator_idname, "mesh_helper.duplicate_copies")
        self.assertIn(
            "class MESH_HELPER_OT_duplicate_copies(bpy.types.Operator):", source
        )
        self.assertIn("bl_idname = 'mesh_helper.duplicate_copies'", source)
        self.assertNotIn(op.id, source)
        self.assertIsNone(errors().addon_error)

    def test_a_custom_node_label_wins(self):
        tree = helpers.new_tree("Main")
        op = self.operator(tree, "Run It")
        op.label = "Cleanup"
        helpers.flush()
        self.assertEqual(op.operator_idname, "mesh_helper.cleanup")

    def test_collisions_get_a_suffix_in_a_fixed_order(self):
        first = helpers.new_tree("A")
        second = helpers.new_tree("B")
        b = self.operator(second, "Go")
        a = self.operator(first, "Go")
        helpers.flush()
        # trees by name, then nodes by name: A's operator comes first
        self.assertEqual(a.operator_idname, "mesh_helper.go")
        self.assertEqual(b.operator_idname, "mesh_helper.go_2")
        self.assertIsNone(errors().addon_error)
        # a single tree preview agrees with the full build
        self.assertIn("class MESH_HELPER_OT_go_2(", helpers.tree_source(second))

    def test_module_names(self):
        trees = [helpers.new_tree(name) for name in ("Main", "main", "class", "3D")]
        helpers.flush()
        self.assertEqual(
            [t.module_name for t in trees], ["main", "main_2", "class_2", "_3d"]
        )
        self.assertIsNone(errors().addon_error)

    def test_function_names_avoid_builtins(self):
        function, _, _ = helpers.new_function("Print", inputs=[("Value", FLOAT)])
        self.assertEqual(function.function_name, "print_2")

    def test_locals_are_plain_and_unique(self):
        tree = helpers.new_tree("Main")
        panel = helpers.add_node(tree, "SNA_Node_Panel")
        first = helpers.add_node(tree, "SNA_Node_Row")
        second = helpers.add_node(tree, "SNA_Node_Row")
        helpers.link(tree, panel.outputs["body"], first.inputs[0])
        helpers.link(tree, first.outputs["Row"], second.inputs[0])
        helpers.flush()
        source = helpers.tree_source(tree)
        self.assertIn("row = self.layout.row(", source)
        self.assertIn("row_2 = row.row(", source)
        self.assertIsNone(errors().addon_error)

    def test_locals_dont_shadow_parameters(self):
        function, group_input, _ = helpers.new_function(
            "Rows", inputs=[("Layout", "ScriptingFlowSocket"), ("Row", FLOAT)]
        )
        next(
            i for i in function.interface.items_tree if i.name == "Layout"
        ).kind = "INTERFACE"
        helpers.flush()
        row = helpers.add_node(function, "SNA_Node_Row")
        helpers.link(function, group_input.outputs[0], row.inputs[0])
        helpers.flush()
        source = helpers.tree_source(function)
        self.assertIn("(row, *,", source)
        self.assertIn("row_2 = layout.row(", source)

    def test_renaming_a_label_renames_the_operator(self):
        tree = helpers.new_tree("Main")
        op = self.operator(tree, "Old")
        helpers.flush()
        self.assertTrue(hasattr(bpy.ops.mesh_helper, "old"))
        op.inputs["label"].value = "New"
        helpers.flush()
        self.assertEqual(op.operator_idname, "mesh_helper.new")
        self.assertIsNone(errors().addon_error)
        self.assertEqual(bpy.ops.mesh_helper.new(), {"FINISHED"})


if __name__ == "__main__":
    unittest.main()
