"""Property options: integer / boolean vectors, string search functions,
Get / Set Functions (get_transform / set_transform) and the attach types
added for bones, nodes, strips, ..."""

import unittest

import bpy
import helpers


def errors():
    return helpers.sn("src.core.errors")


def properties_source():
    files = helpers.sn("src.core.compiler").compile_addon(dev=True)
    return files.get("properties.py", "")


class PropertyOptionsTest(unittest.TestCase):
    def setUp(self):
        helpers.reset_file()
        bpy.context.scene.sna.addon.addon_name = "Option Test"
        self.tree = helpers.new_tree("Main")

    def tearDown(self):
        for tree in list(bpy.data.node_groups):
            bpy.data.node_groups.remove(tree)
        bpy.context.scene.sna.addon.properties.clear()
        helpers.sn("src.core.scheduler").request_full()
        helpers.flush()

    def assertLoaded(self):
        self.assertIsNone(errors().addon_error)
        self.assertEqual(dict(errors().property_errors), {})

    def settings(self):
        return bpy.context.scene.option_test

    def test_integer_and_boolean_vectors(self):
        counts = helpers.add_property("Counts", "VECTOR", vector_type="INTEGER")
        helpers.prop(counts.id).default_vector = (1, 2, 3, 0)
        helpers.add_property("Flags", "VECTOR", vector_type="BOOLEAN", vector_size=2)
        helpers.sn("src.core.scheduler").request_full()
        helpers.flush()
        source = properties_source()
        self.assertIn(
            "bpy.props.IntVectorProperty(name='Counts', default=(1, 2, 3))", source
        )
        self.assertIn("bpy.props.BoolVectorProperty(name='Flags', size=2)", source)
        self.assertLoaded()
        self.assertEqual(tuple(self.settings().counts), (1, 2, 3))
        self.assertEqual(tuple(self.settings().flags), (False, False))
        properties = helpers.sn("src.core.properties")
        flags = helpers.prop(bpy.context.scene.sna.addon.properties[1].id)
        self.assertEqual(properties.socket_type(flags), "ScriptingListSocket")

    def function(self, name, inputs, output, body):
        """A function returning `body` (a Python Expression of its inputs)."""
        tree, group_input, group_output = helpers.new_function(
            name, inputs=inputs, outputs=[("Result", output)]
        )
        expression = helpers.add_node(tree, "SNA_Node_PythonExpression")
        expression.code = body
        helpers.flush()
        for i, (item_name, _) in enumerate(inputs):
            helpers.link(
                tree, group_input.outputs[i], expression.socket("name_" + item_name)
            )
        helpers.link(tree, expression.outputs["result"], group_output.inputs[0])
        return tree

    def test_search_function(self):
        suggest = self.function(
            "Suggest",
            [("text", "ScriptingStringSocket")],
            "ScriptingListSocket",
            "[n for n in ('Red', 'Green', 'Blue') if text.lower() in n.lower()]",
        )
        helpers.add_property("Color Name", "STRING", search_function=suggest)
        source = properties_source()
        self.assertIn("def search_color_name(self, context, edit_text):", source)
        self.assertIn("search=search_color_name", source)
        self.assertLoaded()
        prop = bpy.types.Scene.bl_rna.properties["option_test"].fixed_type
        search = prop.bl_rna.properties["color_name"]
        self.assertTrue(search.is_runtime)  # registered with a callback
        module = __import__(
            bpy.context.scene.sna.addon.module_name + ".properties",
            fromlist=["search_color_name"],
        )
        self.assertEqual(
            module.search_color_name(None, None, "e"), ["Red", "Green", "Blue"]
        )
        self.assertEqual(module.search_color_name(None, None, "gr"), ["Green"])

    def test_get_and_set_functions(self):
        double = self.function(
            "Double",
            [("value", "ScriptingIntegerSocket")],
            "ScriptingIntegerSocket",
            "value * 2",
        )
        clamp = self.function(
            "Even",
            [("value", "ScriptingIntegerSocket")],
            "ScriptingIntegerSocket",
            "value - value % 2",
        )
        helpers.add_property(
            "Steps", "INTEGER", get_function=double, set_function=clamp
        )
        source = properties_source()
        self.assertIn("def get_steps(self, value, is_set):", source)
        self.assertIn("def set_steps(self, new_value, current_value, is_set):", source)
        self.assertIn("get_transform=get_steps, set_transform=set_steps", source)
        self.assertLoaded()
        self.settings().steps = 7  # stored as 6, read doubled
        self.assertEqual(self.settings().steps, 12)

    def test_get_function_needs_an_input(self):
        constant = self.function("Constant", [], "ScriptingIntegerSocket", "3")
        prop = helpers.add_property("Count", "INTEGER", get_function=constant)
        self.assertIn("needs an input", errors().property_errors.get(prop.id, ""))

    def test_new_attach_types(self):
        properties = helpers.sn("src.core.properties")
        for attach_to, owner in (
            ("PoseBone", "context.active_pose_bone"),
            ("Node", "context.active_node"),
            ("Strip", "context.active_strip"),
            ("Brush", None),
        ):
            with self.subTest(attach_to=attach_to):
                prop = helpers.add_property(
                    f"Value {attach_to}",
                    "FLOAT",
                    attach_to=attach_to,
                    in_addon_group=False,
                )
                found = properties.find(prop.id)
                self.assertEqual(properties.owner_expression(found), owner)
                self.assertLoaded()
                self.assertIn(
                    found.prop.python_name or properties.python_name(found),
                    getattr(bpy.types, attach_to).bl_rna.properties,
                )


if __name__ == "__main__":
    unittest.main()
