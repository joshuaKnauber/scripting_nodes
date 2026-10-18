"""Files saved by older versions (core/versioning.py)."""

import unittest

import bpy
import helpers


class RenamedNodesTest(unittest.TestCase):
    """Nodes under their old bl_idnames (nodes/_renamed.py) become the
    renamed node on load."""

    def setUp(self):
        helpers.reset_file()
        bpy.context.scene.sna.addon.addon_name = "Version Test"

    def tearDown(self):
        for tree in list(bpy.data.node_groups):
            bpy.data.node_groups.remove(tree)

    def test_boolean_nodes(self):
        tree = helpers.new_tree()
        old = helpers.add_node(tree, "SNA_BooleanMath", (120, 40))
        old.comparison = "OR"
        old.label = "Either"
        old.socket("b").value = True
        old_id = old.id
        invert = helpers.add_node(tree, "SNA_InvertBoolean")
        printer = helpers.add_node(tree, "SNA_Node_Print")
        operator = helpers.add_node(tree, "SNA_Node_Operator")
        helpers.link(tree, operator.outputs[0], printer.inputs[0])
        helpers.link(tree, old.outputs[0], invert.inputs[0])
        helpers.link(tree, invert.outputs[0], printer.inputs[1])
        tree.data_version = 2
        helpers.sn("src.core.versioning").upgrade([tree])

        idnames = sorted(node.bl_idname for node in tree.nodes)
        self.assertEqual(
            idnames,
            [
                "SNA_Node_BooleanMath",
                "SNA_Node_InvertBoolean",
                "SNA_Node_Operator",
                "SNA_Node_Print",
            ],
        )
        math = next(n for n in tree.nodes if n.bl_idname == "SNA_Node_BooleanMath")
        self.assertEqual(
            (math.comparison, math.label, math.id), ("OR", "Either", old_id)
        )
        self.assertEqual(tuple(math.location), (120, 40))
        self.assertTrue(math.socket("b").value)
        invert = next(n for n in tree.nodes if n.bl_idname == "SNA_Node_InvertBoolean")
        self.assertTrue(invert.inputs[0].is_linked)
        self.assertEqual(invert.inputs[0].links[0].from_node, math)
        self.assertTrue(invert.outputs[0].is_linked)
        helpers.flush()
        self.assertIn("not (False or True)", helpers.tree_source(tree))

    def test_old_types_not_offered(self):
        idnames = {cls.bl_idname for cls in helpers.node_classes()}
        self.assertIn("SNA_Node_BooleanMath", idnames)
        self.assertNotIn("SNA_BooleanMath", idnames)
        graph = helpers.sn("src.mcp_server.tools._common")
        self.assertNotIn(
            "SNA_InvertBoolean", {c.bl_idname for c in graph.node_classes()}
        )


if __name__ == "__main__":
    unittest.main()
