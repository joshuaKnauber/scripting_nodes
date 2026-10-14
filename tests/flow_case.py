"""Base of tests that build a flow after a Trigger, run it and check what
it printed (not a test module itself)."""

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
    """`_sn_helpers` of the loaded add-on (through its package: names in
    sys.modules can be left over from earlier loads)."""
    package = sys.modules[bpy.context.scene.sna.addon.module_name]
    return importlib.import_module(package.__name__ + "._sn_helpers")


def capture(function, *args):
    """What `function(*args)` prints, as lines."""
    out = io.StringIO()
    with contextlib.redirect_stdout(out):
        function(*args)
    return out.getvalue().splitlines()


class FlowTestCase(unittest.TestCase):
    addon_name = "Flow Test"

    def setUp(self):
        helpers.reset_file()
        bpy.context.scene.sna.addon.addon_name = self.addon_name
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
        nexts = [s for s in node.outputs if s.identifier == "next"]
        self.last = nexts[0] if nexts else None
        return node

    def print_value(self, socket, after=None):
        """Print `socket`'s value after the last flow node (or in `after`)."""
        printer = self.add("SNA_Node_Print")
        self.link(after or self.last, printer.inputs[0])
        if after is None:
            self.last = printer.outputs[0]
        self.link(socket, printer.inputs["text"])
        return printer

    def string(self, text):
        node = self.add("SNA_Node_String")
        node.value = text
        return node.outputs["value"]

    def source(self):
        helpers.flush()
        return helpers.tree_source(self.tree)

    def assertBuilt(self):
        helpers.flush()
        self.assertIsNone(errors().addon_error)
        self.assertEqual(dict(errors().node_errors), {})

    def run_trigger(self):
        """Run the trigger, return what it printed (one line per print)."""
        self.assertBuilt()
        namespace, op = self.trigger.operator_idname.split(".")
        return capture(getattr(getattr(bpy.ops, namespace), op))
