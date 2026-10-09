"""Properties as lists (settings/properties.py, core/properties.py): add-on
properties, groups, operator / preferences properties, and the nodes using
them (Get / Set Property, fields, On Property Update)."""

import unittest

import bpy
import helpers


def errors():
    return helpers.sn("src.core.errors")


def files():
    return helpers.sn("src.core.compiler").compile_addon(dev=True)


def properties_source():
    return files().get("addon/properties.py", "")


def run_trigger(trigger):
    namespace, op = trigger.operator_idname.split(".")
    return getattr(getattr(bpy.ops, namespace), op)()


class PropertiesTest(unittest.TestCase):
    def setUp(self):
        helpers.reset_file()
        bpy.context.scene.sna.addon.addon_name = "Prop Test"
        self.tree = helpers.new_tree("Main")

    def tearDown(self):
        for tree in list(bpy.data.node_groups):
            bpy.data.node_groups.remove(tree)
        bpy.context.scene.sna.addon.properties.clear()
        helpers.sn("src.core.scheduler").request_full()
        helpers.flush()

    def assertLoaded(self):
        self.assertIsNone(errors().addon_error)

    def add(self, idname, location=(0, 0)):
        return helpers.add_node(self.tree, idname, location)

    # -- add-on properties --------------------------------------------------

    def test_addon_property_in_the_addon_group(self):
        helpers.add_property("Count", "INTEGER", default_int=3)
        source = properties_source()
        self.assertIn(
            "class PROP_TEST_PG_scene_properties(bpy.types.PropertyGroup):", source
        )
        self.assertIn(
            "    count: bpy.props.IntProperty(name='Count', default=3)", source
        )
        self.assertIn(
            "bpy.types.Scene.prop_test = "
            "bpy.props.PointerProperty(type=PROP_TEST_PG_scene_properties)",
            source,
        )
        self.assertIn("del bpy.types.Scene.prop_test", source)
        self.assertLoaded()
        self.assertEqual(bpy.context.scene.prop_test.count, 3)

    def test_direct_and_other_attach_types(self):
        helpers.add_property("Speed", "FLOAT", in_addon_group=False, default_float=2.5)
        helpers.add_property("Tag", "STRING", attach_to="Object")
        source = properties_source()
        self.assertIn(
            "bpy.types.Scene.speed = bpy.props.FloatProperty(name='Speed', default=2.5)",
            source,
        )
        self.assertIn("bpy.types.Object.prop_test = bpy.props.PointerProperty(", source)
        self.assertLoaded()
        self.assertEqual(bpy.context.scene.speed, 2.5)
        self.assertTrue(hasattr(bpy.types.Object, "prop_test"))

    def test_every_type_loads_with_defaults_left_out(self):
        for name, kind in (
            ("Flag", "BOOLEAN"),
            ("Count", "INTEGER"),
            ("Amount", "FLOAT"),
            ("Offset", "VECTOR"),
            ("Label", "STRING"),
            ("Mode", "ENUM"),
            ("Target", "POINTER"),
        ):
            helpers.add_property(name, kind)
        source = properties_source()
        self.assertIn("flag: bpy.props.BoolProperty(name='Flag')", source)
        self.assertIn("offset: bpy.props.FloatVectorProperty(name='Offset')", source)
        self.assertIn(
            "target: bpy.props.PointerProperty(name='Target', type=bpy.types.Object)",
            source,
        )
        self.assertNotIn("options=", source)
        self.assertLoaded()
        settings = bpy.context.scene.prop_test
        self.assertEqual(settings.mode, "Option A")
        self.assertEqual(tuple(settings.offset), (0.0, 0.0, 0.0))

    def test_settings_become_arguments(self):
        helpers.add_property(
            "Amount",
            "FLOAT",
            default_float=0.5,
            use_min=True,
            min_value=0.0,
            use_max=True,
            max_value=1.0,
            subtype_float="FACTOR",
            option_animatable=False,
        )
        helpers.add_property("Color", "VECTOR", vector_size=4, subtype_vector="COLOR")
        source = properties_source()
        self.assertIn(
            "amount: bpy.props.FloatProperty(name='Amount', default=0.5, min=0.0, "
            "max=1.0, subtype='FACTOR', options=set())",
            source,
        )
        self.assertIn("size=4", source)
        self.assertLoaded()

    def test_python_names_are_unique_and_can_be_pinned(self):
        helpers.add_property("Count", "INTEGER")
        helpers.add_property("count", "INTEGER")
        helpers.add_property("Old Label", "INTEGER", python_name="pinned")
        source = properties_source()
        self.assertIn("    count: ", source)
        self.assertIn("    count_2: ", source)
        self.assertIn("    pinned: ", source)
        self.assertLoaded()

    # -- groups -------------------------------------------------------------

    def test_groups_pointer_and_collection(self):
        item = helpers.add_property("Item", "GROUP").id
        helpers.add_property(
            "Weight", "FLOAT", owner=helpers.prop(item), default_float=1.5
        )
        helpers.add_property(
            "Main Item", "POINTER", pointer_source="GROUP"
        ).group_id = item
        helpers.add_property("Items", "COLLECTION").group_id = item
        helpers.flush()
        source = properties_source()
        self.assertLess(
            source.index("class PROP_TEST_PG_item("),
            source.index("class PROP_TEST_PG_scene_properties("),
        )
        self.assertIn(
            "main_item: bpy.props.PointerProperty(name='Main Item', type=PROP_TEST_PG_item)",
            source,
        )
        # `items` is taken (PropertyGroup.items())
        self.assertIn(
            "items_2: bpy.props.CollectionProperty(name='Items', type=PROP_TEST_PG_item)",
            source,
        )
        self.assertLoaded()
        settings = bpy.context.scene.prop_test
        self.assertEqual(settings.main_item.weight, 1.5)
        settings.items_2.add()
        self.assertEqual(len(settings.items_2), 1)

    def test_nested_groups_are_defined_in_order(self):
        outer = helpers.add_property("Outer", "GROUP").id
        inner = helpers.add_property("Inner", "GROUP").id
        nested = helpers.add_property(
            "Children", "COLLECTION", owner=helpers.prop(outer)
        )
        nested.group_id = inner
        helpers.flush()
        source = properties_source()
        self.assertLess(
            source.index("class PROP_TEST_PG_inner("),
            source.index("class PROP_TEST_PG_outer("),
        )
        self.assertLoaded()

    def test_missing_group_is_reported_on_the_property(self):
        items = helpers.add_property("Items", "COLLECTION").id
        helpers.add_property("Count", "INTEGER")
        self.assertIn("group", errors().property_errors.get(items, ""))
        self.assertNotIn("items:", properties_source())
        self.assertLoaded()

    # -- enums --------------------------------------------------------------

    def test_enum_static_items(self):
        mode = helpers.add_property("Mode", "ENUM")
        mode.enum_items[1].description = "Second"
        mode.default_enum = "Option B"
        helpers.flush()
        source = properties_source()
        self.assertIn("('Option A', 'Option A', '')", source)
        self.assertIn("('Option B', 'Option B', 'Second')", source)
        self.assertIn("default='Option B'", source)
        self.assertLoaded()
        settings = bpy.context.scene.prop_test
        self.assertEqual(settings.mode, "Option B")

    def test_enum_items_from_a_function(self):
        function, _, group_output = helpers.new_function(
            "Colors", outputs=[("Items", "ScriptingListSocket")]
        )
        create = helpers.add_node(function, "SNA_Node_CreateList")
        for value in ("Red", "Green"):
            text = helpers.add_node(function, "SNA_Node_String")
            text.value = value
            helpers.link(function, text.outputs[0], create.inputs[-1])
        helpers.link(function, create.outputs["list"], group_output.inputs[0])
        helpers.add_property("Color", "ENUM", items_function=function)
        source = properties_source()
        self.assertIn("def color_items(self, context):", source)
        self.assertIn("from .colors import colors", source)
        self.assertIn("items=color_items", source)
        self.assertLoaded()
        settings = bpy.context.scene.prop_test
        settings.color = "Green"
        self.assertEqual(settings.color, "Green")

    def test_pointer_poll_function(self):
        function, group_input, group_output = helpers.new_function(
            "Visible",
            inputs=[("Item", "ScriptingBlendDataSocket")],
            outputs=[("Allowed", "ScriptingBooleanSocket")],
        )
        hidden = helpers.add_node(function, "SNA_Node_GetProperty")
        hidden.mode = "BLENDER"
        hidden.setup_from_path("", "hide_viewport", True)
        helpers.flush()
        helpers.link(function, group_input.outputs[0], hidden.inputs["Data"])
        helpers.link(function, hidden.outputs["Value"], group_output.inputs[0])
        helpers.add_property("Target", "POINTER", poll_function=function)
        source = properties_source()
        self.assertIn("def poll_target(self, object):", source)
        self.assertIn("return bool(visible(object, self=self))", source)
        self.assertIn("poll=poll_target", source)
        self.assertLoaded()

    # -- operator / preferences properties -----------------------------------

    def test_operator_properties_are_annotations_and_outputs(self):
        op = self.add("SNA_Node_Operator")
        prop = helpers.add_property("Text", "STRING", owner=op, default_string="hi")
        self.assertIn("prop_" + prop.id, [s.identifier for s in op.outputs])
        printer = self.add("SNA_Node_Print")
        helpers.link(self.tree, op.outputs["Execute"], printer.inputs[0])
        helpers.link(self.tree, op.outputs["Text"], printer.inputs["text"])
        helpers.flush()
        source = helpers.tree_source(self.tree)
        self.assertIn(
            "    text: bpy.props.StringProperty(name='Text', default='hi')", source
        )
        self.assertIn("sn_print(self.text)", source)
        self.assertLoaded()
        namespace, name = op.operator_idname.split(".")
        rna = getattr(getattr(bpy.ops, namespace), name).get_rna_type()
        self.assertIn("text", rna.properties.keys())

    def test_copied_operator_gets_its_own_property_ids(self):
        op = self.add("SNA_Node_Operator")
        prop = helpers.add_property("Text", "STRING", owner=op)
        copy = self.tree.nodes.new("SNA_Node_Operator")
        copy.properties.add().id = prop.id  # what Duplicate does
        helpers.sn("src.core.scheduler").request_full()
        helpers.flush()
        self.assertNotEqual(copy.properties[0].id, prop.id)

    def test_preferences(self):
        prefs = self.add("SNA_Node_Preferences")
        prop = helpers.add_property("Verbose", "BOOLEAN", owner=prefs)
        checkbox = self.add("SNA_Node_Checkbox")
        helpers.link(self.tree, prefs.outputs["Draw"], checkbox.inputs[0])
        helpers.pick_property(checkbox, prop)
        source = helpers.tree_source(self.tree)
        self.assertIn("bpy.types.AddonPreferences", source)
        self.assertIn("    verbose: bpy.props.BoolProperty(name='Verbose')", source)
        self.assertIn(
            "self.layout.prop(context.preferences.addons[__package__.rsplit('.', 1)[0]]"
            ".preferences, 'verbose')",
            source,
        )
        self.assertLoaded()

    # -- using properties -----------------------------------------------------

    def test_get_and_set_on_the_scene_by_default(self):
        count = helpers.add_property("Count", "INTEGER")
        trigger = self.add("SNA_Node_Trigger")
        setter = self.add("SNA_Node_SetProperty")
        getter = self.add("SNA_Node_GetProperty")
        helpers.pick_property(setter, count)
        helpers.pick_property(getter, count)
        self.assertEqual(setter.inputs["Value"].bl_idname, "ScriptingIntegerSocket")
        self.assertEqual(getter.outputs["Value"].bl_idname, "ScriptingIntegerSocket")
        self.assertEqual(getter.socket("data").name, "Scene")
        setter.inputs["Value"].value = 42
        printer = self.add("SNA_Node_Print")
        helpers.link(self.tree, trigger.outputs[0], setter.inputs[0])
        helpers.link(self.tree, setter.outputs[0], printer.inputs[0])
        helpers.link(self.tree, getter.outputs["Value"], printer.inputs[1])
        helpers.flush()
        source = helpers.tree_source(self.tree)
        self.assertIn("context.scene.prop_test.count = 42", source)
        self.assertIn("str(context.scene.prop_test.count)", source)
        self.assertLoaded()
        self.assertEqual(run_trigger(trigger), {"FINISHED"})
        self.assertEqual(bpy.context.scene.prop_test.count, 42)

    def test_connected_owner_wins(self):
        tag = helpers.add_property("Tag", "STRING", attach_to="Object")
        trigger = self.add("SNA_Node_Trigger")
        objects = self.add("SNA_Node_GetProperty")
        objects.mode = "BLENDER"
        objects.setup_from_path("bpy.context", "active_object", False)
        setter = self.add("SNA_Node_SetProperty")
        helpers.pick_property(setter, tag)
        helpers.link(self.tree, trigger.outputs[0], setter.inputs[0])
        helpers.link(self.tree, objects.outputs["Value"], setter.socket("data"))
        helpers.flush()
        self.assertIn(
            "bpy.context.active_object.prop_test.tag = ''",
            helpers.tree_source(self.tree),
        )
        self.assertLoaded()

    def test_group_member_needs_the_item(self):
        item = helpers.add_property("Item", "GROUP").id
        weight = helpers.add_property("Weight", "FLOAT", owner=helpers.prop(item))
        trigger = self.add("SNA_Node_Trigger")
        getter = self.add("SNA_Node_GetProperty")
        helpers.pick_property(getter, weight)
        self.assertEqual(getter.socket("data").name, "Item")
        printer = self.add("SNA_Node_Print")
        helpers.link(self.tree, trigger.outputs[0], printer.inputs[0])
        helpers.link(self.tree, getter.outputs["Value"], printer.inputs[1])
        helpers.flush()
        self.assertIn("Connect the Item", errors().node_errors.get(getter.id, ""))
        self.assertLoaded()

    def test_picker_by_name(self):
        flag = helpers.add_property("Flag", "BOOLEAN").id
        helpers.add_property("Count", "INTEGER")
        checkbox = self.add("SNA_Node_Checkbox")
        checkbox.prop = "Flag"
        self.assertEqual(checkbox.prop_id, flag)
        self.assertEqual(checkbox.prop, "Flag")
        names = [e.name for e in bpy.context.scene.sna.refs_props_boolean]
        self.assertEqual(names, ["Flag"])  # a checkbox only offers booleans

    def test_on_property_update(self):
        count = helpers.add_property("Count", "INTEGER").id
        flag = helpers.add_property("Flag", "BOOLEAN")
        update = self.add("SNA_Node_OnPropertyUpdate")
        helpers.pick_property(update, helpers.prop(count))
        setter = self.add("SNA_Node_SetProperty")
        helpers.pick_property(setter, flag)
        setter.inputs["Value"].value = True
        helpers.link(self.tree, update.outputs[0], setter.inputs[0])
        helpers.link(self.tree, update.outputs["Owner"], setter.socket("data"))
        helpers.flush()
        source = helpers.tree_source(self.tree)
        self.assertIn("def on_count_update(self, context):", source)
        self.assertIn("self.id_data.prop_test.flag = True", source)
        props = properties_source()
        self.assertIn("from .main import on_count_update", props)
        self.assertIn("update=update_count", props)
        self.assertLoaded()
        settings = bpy.context.scene.prop_test
        settings.count = 5
        self.assertTrue(settings.flag)

    def test_button_gets_operator_arguments(self):
        op = self.add("SNA_Node_Operator")
        helpers.add_property("Amount", "INTEGER", owner=op)
        helpers.add_property("Offset", "VECTOR", owner=op, vector_size=2)
        panel = self.add("SNA_Node_Panel")
        button = self.add("SNA_Node_Button")
        helpers.link(self.tree, panel.outputs["Interface"], button.inputs[0])
        button.operator_sn = helpers.sn("src.core.references").display_name(op)
        helpers.flush()
        button.socket("arg_amount").value = 5
        self.assertEqual(button.socket("arg_offset").dimension, "2")
        helpers.flush()
        source = helpers.tree_source(self.tree)
        self.assertIn("op.amount = 5", source)
        self.assertLoaded()


if __name__ == "__main__":
    unittest.main()
