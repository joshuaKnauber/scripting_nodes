"""Script node: scripts are modules of the add-on, the node calls run()."""

import sys
import unittest

import bpy
import helpers

SCALE = '''import bpy


def run(obj: bpy.types.Object, factor: float = 2.0, context=None) -> float:
    """Scale an object."""
    obj.scale = (factor,) * 3
    context.scene["scaled"] = obj.name
    return factor * 10
'''

STATS = """def run(context) -> tuple[int, str]:
    count = len(context.scene.objects)
    name = context.scene.name
    return count, name
"""


def errors():
    return helpers.sn("src.core.errors")


def run(node):
    """Call the operator of a Trigger node."""
    namespace, name = node.operator_idname.split(".")
    return getattr(getattr(bpy.ops, namespace), name)()


def module_name():
    return bpy.context.scene.sna.addon.module_name


def text(name, body):
    text = bpy.data.texts.new(name)
    text.write(body)
    return text


class ScriptNodeTest(unittest.TestCase):
    def setUp(self):
        helpers.reset_file()
        bpy.context.scene.sna.addon.addon_name = "Script Test"

    def tearDown(self):
        for tree in list(bpy.data.node_groups):
            bpy.data.node_groups.remove(tree)
        helpers.sn("src.core.scheduler").request_full()
        helpers.flush()

    def assertLoaded(self):
        self.assertIsNone(errors().addon_error)

    def script(self, tree, source_text, function="run"):
        node = helpers.add_node(tree, "SNA_Node_Script")
        node.text_block = source_text
        node.function_name = function
        return node

    def triggered(self, source, name="tools.py"):
        tree = helpers.new_tree()
        trigger = helpers.add_node(tree, "SNA_Node_Trigger")
        script = self.script(tree, text(name, source))
        helpers.flush()
        if len(script.inputs):
            helpers.link(tree, trigger.outputs[0], script.inputs[0])
        helpers.flush()
        return tree, trigger, script

    # -- sockets from the signature ---------------------------------------------

    def test_signature_declares_sockets(self):
        tree, _, script = self.triggered(SCALE)
        inputs = [(s.identifier, s.bl_idname, s.name) for s in script.inputs]
        self.assertEqual(
            inputs,
            [
                ("flow", "ScriptingFlowSocket", "Program"),
                ("obj", "ScriptingBlendDataSocket", "Obj"),
                ("factor", "ScriptingFloatSocket", "Factor"),
            ],
        )
        self.assertEqual(script.socket("factor").value, 2.0)
        outputs = [(s.identifier, s.bl_idname) for s in script.outputs]
        self.assertEqual(
            outputs,
            [("next", "ScriptingFlowSocket"), ("output_0", "ScriptingFloatSocket")],
        )
        self.assertEqual(script.draw_label(), "Script: Tools")

        script.text_block = text("stats.py", STATS)
        names = [(s.identifier, s.name) for s in script.outputs]
        self.assertEqual(
            names, [("next", "Program"), ("output_0", "Count"), ("output_1", "Name")]
        )
        self.assertEqual(script.outputs[1].bl_idname, "ScriptingIntegerSocket")
        self.assertEqual(script.outputs[2].bl_idname, "ScriptingStringSocket")
        self.assertEqual([s.identifier for s in script.inputs], ["flow"])

    def test_template_fills_an_empty_text(self):
        tree = helpers.new_tree()
        script = self.script(tree, text("Text", ""))
        helpers.flush()
        self.assertEqual([s.identifier for s in script.outputs], ["next"])
        bpy.ops.sna.new_script(node_id=script.id)
        self.assertEqual(script.text_block.name, "Text")  # filled, not replaced
        helpers.flush()
        self.assertEqual(script.socket("name").value, "World")
        # without a text, a new one
        other = helpers.add_node(tree, "SNA_Node_Script")
        bpy.ops.sna.new_script(node_id=other.id)
        self.assertIn("def run(", other.text_block.as_string())

    def test_without_a_function_the_code_goes_in_the_flow(self):
        source = "# count\ncontext.scene['runs'] = context.scene.get('runs', 0) + 1\n"
        tree, trigger, script = self.triggered(source, "count.py")
        self.assertEqual([s.identifier for s in script.inputs], ["flow"])
        self.assertEqual([s.identifier for s in script.outputs], ["next"])
        code = helpers.tree_source(tree)
        self.assertIn(
            "        # count\n"
            "        context.scene['runs'] = context.scene.get('runs', 0) + 1",
            code,
        )
        self.assertNotIn("scripts/count.py", helpers.addon_files())
        self.assertLoaded()
        self.assertNotIn("runs", bpy.context.scene)  # not when it loads
        run(trigger)
        run(trigger)
        self.assertEqual(bpy.context.scene["runs"], 2)

    def test_errors_in_inline_code_show_on_the_node(self):
        tree, trigger, script = self.triggered("x = 1 / 0\n", "broken.py")
        self.assertLoaded()
        with self.assertRaises(RuntimeError):
            run(trigger)
        self.assertIn("ZeroDivisionError", errors().node_message(script.id) or "")

    def test_inline_code_drawing_ui(self):
        tree = helpers.new_tree()
        panel = helpers.add_node(tree, "SNA_Node_Panel")
        script = self.script(tree, text("ui.py", "layout.label(text='Hi')\n"), "")
        helpers.flush()
        self.assertEqual(script.inputs[0].kind, "INTERFACE")
        helpers.link(tree, panel.outputs["body"], script.inputs[0])
        helpers.flush()
        code = helpers.tree_source(tree)
        self.assertIn("layout = self.layout\n        layout.label(text='Hi')", code)
        self.assertLoaded()

    def test_pick_any_function(self):
        source = (
            SCALE + "\n\ndef double(value: int = 2) -> int:\n    return value * 2\n"
        )
        tree = helpers.new_tree()
        script = self.script(tree, text("tools.py", source), "")
        helpers.flush()
        self.assertEqual(script.script_functions(), ["run", "double"])
        self.assertEqual(script.function, ":code")
        self.assertEqual([s.identifier for s in script.inputs], ["flow"])
        script.function = "double"
        self.assertEqual(script.function_name, "double")
        helpers.flush()
        trigger = helpers.add_node(tree, "SNA_Node_Trigger")
        helpers.link(tree, trigger.outputs[0], script.inputs[0])
        helpers.flush()
        self.assertEqual(script.socket("value").value, 2)
        self.assertIn("tools.double(value=2)", helpers.tree_source(tree))
        # still picked when the functions move
        script.text_block.clear()
        script.text_block.write("def double(value: int = 2) -> int:\n    return 4\n")
        self.assertEqual(script.function, "double")
        script.text_block.clear()
        script.text_block.write(SCALE)
        self.assertEqual(script.function, ":code")  # gone

    def test_add_to_addon(self):
        """Scripts with classes are added to the add-on unless the node is
        told otherwise; the dropdown shows it."""
        source = "import bpy\n\n\nclass HELLO_OT_x(bpy.types.Operator):\n    bl_idname = 'hello.x'\n    bl_label = 'X'\n"
        tree = helpers.new_tree()
        script = self.script(tree, text("hello.py", source), "")
        helpers.flush()
        self.assertEqual(script.function, ":addon")
        self.assertEqual(len(script.inputs) + len(script.outputs), 0)
        self.assertTrue(hasattr(bpy.types, "HELLO_OT_x"))
        script.function = ":code"
        helpers.flush()
        self.assertEqual([s.identifier for s in script.inputs], ["flow"])
        self.assertNotIn("scripts/hello.py", helpers.addon_files())
        # plain code can be added too: it runs once, when the add-on loads
        plain = self.script(tree, text("once.py", "x = 1\n"), "")
        self.assertEqual(plain.function, ":code")
        plain.function = ":addon"
        helpers.flush()
        self.assertIn("scripts/once.py", helpers.addon_files())
        self.assertLoaded()

    def test_data_only(self):
        source = "def double(value: int = 2) -> int:\n    return value * 2\n"
        tree = helpers.new_tree()
        trigger = helpers.add_node(tree, "SNA_Node_Trigger")
        script = self.script(tree, text("maths.py", source), "double")
        script.data_only = True
        helpers.flush()
        self.assertEqual([s.identifier for s in script.inputs], ["value"])
        self.assertEqual([s.identifier for s in script.outputs], ["output_0"])
        p = helpers.add_node(tree, "SNA_Node_Print")
        helpers.link(tree, trigger.outputs[0], p.inputs[0])
        helpers.link(tree, script.outputs[0], p.inputs[1])
        helpers.flush()
        self.assertIn("sn_print(str(maths.double(value=2)))", helpers.tree_source(tree))
        self.assertLoaded()

    def test_old_nodes_call_run(self):
        tree = helpers.new_tree()
        script = self.script(tree, text("tools.py", SCALE), "")
        tree.data_version = 1
        helpers.sn("src.core.versioning").upgrade([tree])
        self.assertEqual(script.function_name, "run")

    def test_run_is_called(self):
        tree, trigger, script = self.triggered(SCALE)
        data = helpers.add_node(tree, "SNA_Node_BlendData")
        data.paste_path("bpy.data.objects['Thing']")
        p = helpers.add_node(tree, "SNA_Node_Print")
        cube = bpy.data.objects.new("Thing", None)
        bpy.context.scene.collection.objects.link(cube)
        helpers.link(tree, data.outputs[0], script.socket("obj"))
        script.socket("factor").value = 3.0
        helpers.link(tree, script.outputs[0], p.inputs[0])
        helpers.link(tree, script.outputs[1], p.inputs[1])
        helpers.flush()

        code = helpers.tree_source(tree)
        self.assertIn("from ..scripts import tools", code)
        self.assertIn("result = tools.run(obj=", code)
        self.assertIn("factor=3.0, context=context)", code)
        self.assertIn("sn_print(str(result))", code)
        files = helpers.addon_files()
        # the script, unchanged
        self.assertEqual(files["scripts/tools.py"], SCALE)
        self.assertLoaded()
        self.assertEqual(run(trigger), {"FINISHED"})
        self.assertEqual(bpy.context.scene["scaled"], "Thing")
        self.assertEqual(tuple(cube.scale), (3.0, 3.0, 3.0))

    def test_several_returns(self):
        tree, trigger, script = self.triggered(STATS, "stats.py")
        p = helpers.add_node(tree, "SNA_Node_Print")
        helpers.link(tree, script.outputs[0], p.inputs[0])
        helpers.link(tree, script.outputs[2], p.inputs[1])
        helpers.flush()
        self.assertIn(
            "count, name = stats.run(context=context)", helpers.tree_source(tree)
        )
        self.assertLoaded()
        self.assertEqual(run(trigger), {"FINISHED"})

    def test_layout_parameter_draws_ui(self):
        source = "def run(layout, title: str = 'Hi'):\n    layout.label(text=title)\n"
        tree = helpers.new_tree()
        panel = helpers.add_node(tree, "SNA_Node_Panel")
        script = self.script(tree, text("ui.py", source))
        helpers.flush()
        self.assertEqual(script.inputs[0].kind, "INTERFACE")
        helpers.link(tree, panel.outputs["body"], script.inputs[0])
        helpers.flush()
        self.assertIn(
            "ui.run(layout=self.layout, title='Hi')", helpers.tree_source(tree)
        )
        self.assertLoaded()

    # -- the module ---------------------------------------------------------------

    def test_module_only_with_own_register(self):
        source = """import bpy


class HELLO_OT_wave(bpy.types.Operator):
    bl_idname = "hello.wave"
    bl_label = "Wave"

    def execute(self, context):
        context.scene["waved"] = True
        return {"FINISHED"}


def register():
    bpy.utils.register_class(HELLO_OT_wave)
    bpy.app.driver_namespace["sn_script_test"] = "registered"


def unregister():
    bpy.utils.unregister_class(HELLO_OT_wave)
    bpy.app.driver_namespace["sn_script_test"] = "unregistered"
"""
        tree = helpers.new_tree()
        script = self.script(tree, text("hello.py", source))
        helpers.flush()
        self.assertEqual(len(script.inputs) + len(script.outputs), 0)
        self.assertLoaded()
        self.assertEqual(bpy.app.driver_namespace["sn_script_test"], "registered")
        self.assertEqual(bpy.ops.hello.wave(), {"FINISHED"})
        self.assertTrue(bpy.context.scene["waved"])

        bpy.data.node_groups.remove(tree)
        helpers.sn("src.core.scheduler").request_full()
        helpers.flush()
        self.assertEqual(bpy.app.driver_namespace["sn_script_test"], "unregistered")
        self.assertFalse(hasattr(bpy.types, "HELLO_OT_wave"))

    def test_classes_without_register_are_registered(self):
        source = """import bpy
from bpy.types import Panel


class HELLO_PT_auto(Panel):
    bl_label = "Auto"
    bl_space_type = "VIEW_3D"
    bl_region_type = "UI"

    def draw(self, context):
        self.layout.label(text="auto")
"""
        tree = helpers.new_tree()
        self.script(tree, text("auto.py", source))
        helpers.flush()
        self.assertLoaded()
        self.assertTrue(hasattr(bpy.types, "HELLO_PT_auto"))

    def test_nodes_share_a_scripts_module(self):
        tree, _, first = self.triggered(SCALE)
        other = helpers.new_tree("Other")
        trigger = helpers.add_node(other, "SNA_Node_Trigger")
        second = self.script(other, first.text_block)
        helpers.link(other, trigger.outputs[0], second.inputs[0])
        helpers.flush()
        scripts = [rel for rel in helpers.addon_files() if rel.startswith("scripts/")]
        self.assertEqual(sorted(scripts), ["scripts/__init__.py", "scripts/tools.py"])
        self.assertIn("tools.run(", helpers.tree_source(other))
        self.assertLoaded()

    def test_names_dont_collide(self):
        # a function named like the script's module
        tree, _, script = self.triggered(SCALE)
        function, _, _ = helpers.new_function("Tools")
        helpers.flush()
        code = helpers.tree_source(tree)
        self.assertIn("from ..scripts import tools as tools_2", code)
        self.assertIn("tools_2.run(", code)
        self.assertLoaded()

    def test_removed_script_module_is_deleted(self):
        tree, _, script = self.triggered(SCALE)
        self.assertLoaded()
        tree.nodes.remove(script)
        helpers.sn("src.core.scheduler").request_full()
        helpers.flush()
        self.assertNotIn("scripts/tools.py", helpers.addon_files())
        self.assertNotIn(f"{module_name()}.scripts.tools", sys.modules)

    def test_export_contains_scripts(self):
        self.triggered(SCALE)
        files = helpers.sn("src.core.compiler").compile_addon(dev=False)
        self.assertEqual(files["scripts/tools.py"], SCALE)

    # -- editing and errors --------------------------------------------------------

    def test_text_edits_update_sockets(self):
        tree, _, script = self.triggered(SCALE)
        scheduler = helpers.sn("src.core.scheduler")
        scheduler.run_watchers()  # records the current source
        source = script.text_block
        source.clear()
        source.write(SCALE.replace("factor: float = 2.0", "factor: int = 4"))
        scheduler.run_watchers()
        helpers.flush()
        self.assertEqual(script.socket("factor").bl_idname, "ScriptingIntegerSocket")
        self.assertEqual(script.socket("factor").value, 4)

    def test_syntax_error_keeps_sockets(self):
        tree, trigger, script = self.triggered(SCALE)
        p = helpers.add_node(tree, "SNA_Node_Print")
        helpers.link(tree, script.outputs[1], p.inputs[1])
        source = script.text_block
        source.clear()
        source.write("def run(:\n    pass\n")
        script.mark_dirty()
        helpers.flush()
        self.assertIn("Line 1", errors().node_message(script.id))
        self.assertTrue(script.outputs[1].is_linked)
        self.assertNotIn("scripts/tools.py", helpers.addon_files())
        self.assertLoaded()  # the rest of the add-on still loads

        source.clear()
        source.write(SCALE)
        script.mark_dirty()
        helpers.flush()
        self.assertFalse(errors().node_message(script.id))
        self.assertTrue(script.outputs[1].is_linked)

    def test_load_error_is_shown_on_the_script_node(self):
        source = "raise ValueError('broken')\n\n\ndef run():\n    pass\n"
        tree, trigger, script = self.triggered(source)
        self.assertIn("broken", errors().addon_error)
        self.assertIn(script.id, errors().load_errors)
        self.assertNotIn(trigger.id, errors().load_errors)


if __name__ == "__main__":
    unittest.main()
