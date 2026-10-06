"""Every node must produce code that compiles - alone, chained, and as data source."""

import unittest

import helpers

PROGRAM = {"ScriptingProgramSocket", "ScriptingLogicSocket"}
INTERFACE = {"ScriptingInterfaceSocket"}


def first(sockets, idnames):
    for s in sockets:
        if s.bl_idname in idnames:
            return s
    return None


def data_outputs(node):
    return [s for s in node.outputs if getattr(s, "socket_type", None) == "DATA"]


class NodeCompileTest(unittest.TestCase):
    def setUp(self):
        helpers.reset_file()

    def assertCompiles(self, tree, label):
        source = helpers.tree_source(tree)
        try:
            compile(source, f"<{label}>", "exec")
        except SyntaxError as e:
            numbered = "\n".join(
                f"{i + 1:4d} {line}" for i, line in enumerate(source.splitlines())
            )
            self.fail(f"{label}: {e}\n{numbered}")

    def test_single_node(self):
        for cls in helpers.node_classes():
            with self.subTest(node=cls.bl_idname):
                helpers.reset_file()
                tree = helpers.new_tree_for(cls)
                helpers.add_node(tree, cls.bl_idname)
                helpers.flush()
                self.assertCompiles(tree, cls.bl_idname)

    def test_program_chain(self):
        """Trigger -> Node -> Print -> Print: catches broken indentation of `next`."""
        for cls in helpers.node_classes():
            helpers.reset_file()
            tree = helpers.new_tree_for(cls)
            node = helpers.add_node(tree, cls.bl_idname)
            inp = first(node.inputs, PROGRAM)
            out = first(node.outputs, PROGRAM)
            if not inp or not out:
                continue
            with self.subTest(node=cls.bl_idname):
                trigger = helpers.add_node(tree, "SNA_Node_Trigger")
                p1 = helpers.add_node(tree, "SNA_Node_Print")
                p2 = helpers.add_node(tree, "SNA_Node_Print")
                helpers.link(tree, trigger.outputs[0], inp)
                helpers.link(tree, out, p1.inputs[0])
                helpers.link(tree, p1.outputs[0], p2.inputs[0])
                helpers.flush()
                self.assertCompiles(tree, cls.bl_idname)

    def test_interface_chain(self):
        """Panel -> Node -> Label -> Label."""
        for cls in helpers.node_classes():
            helpers.reset_file()
            tree = helpers.new_tree_for(cls)
            node = helpers.add_node(tree, cls.bl_idname)
            inp = first(node.inputs, INTERFACE)
            out = first(node.outputs, INTERFACE)
            if not inp or not out:
                continue
            with self.subTest(node=cls.bl_idname):
                panel = helpers.add_node(tree, "SNA_Node_Panel")
                l1 = helpers.add_node(tree, "SNA_Node_Label")
                l2 = helpers.add_node(tree, "SNA_Node_Label")
                helpers.link(tree, panel.outputs["Interface"], inp)
                helpers.link(tree, out, l1.inputs[0])
                helpers.link(tree, l1.outputs[0], l2.inputs[0])
                helpers.flush()
                self.assertCompiles(tree, cls.bl_idname)

    def test_data_source(self):
        """Every data output can feed a Print node."""
        for cls in helpers.node_classes():
            helpers.reset_file()
            tree = helpers.new_tree_for(cls)
            node = helpers.add_node(tree, cls.bl_idname)
            outs = data_outputs(node)
            if not outs:
                continue
            with self.subTest(node=cls.bl_idname):
                trigger = helpers.add_node(tree, "SNA_Node_Trigger")
                prev = trigger.outputs[0]
                for out in outs:
                    p = helpers.add_node(tree, "SNA_Node_Print")
                    helpers.link(tree, prev, p.inputs[0])
                    helpers.link(tree, out, p.inputs[1])
                    prev = p.outputs[0]
                helpers.flush()
                self.assertCompiles(tree, cls.bl_idname)
