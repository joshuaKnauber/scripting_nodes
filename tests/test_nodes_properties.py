"""Property nodes, Property Groups, Preferences and Get/Set Property."""

import unittest

import bpy
import helpers


def refs():
    return helpers.sn("src.core.references")


def node_errors():
    return helpers.sn("src.core.errors").node_errors


def pick(node, prop, target):
    """Point reference field `prop` of `node` at `target`."""
    setattr(node, prop, refs().display_name(target))


def attach(container, prop_node):
    entry = container.class_body_properties.add()
    entry.prop = refs().display_name(prop_node)


def source_of(tree):
    """Generated module source, unformatted (no line wrapping)."""
    return helpers.sn("src.core.compiler").compile_tree(tree, pretty=False)


def run_trigger(trigger):
    namespace, op = trigger.operator_idname.split(".")
    return getattr(getattr(bpy.ops, namespace), op)()


class PropertyNodesTest(unittest.TestCase):
    def setUp(self):
        helpers.reset_file()

    def tearDown(self):
        for tree in list(bpy.data.node_groups):
            bpy.data.node_groups.remove(tree)
        helpers.sn("src.core.scheduler").request_full()
        helpers.flush()

    def assertLoaded(self):
        self.assertIsNone(helpers.sn("src.core.errors").addon_error)

    # -- registration ---------------------------------------------------------

    def test_scene_property_is_registered(self):
        tree = helpers.new_tree()
        prop = helpers.add_node(tree, "SNA_Node_FloatProperty")
        prop.prop_default = 2.5
        helpers.flush()
        name = prop.prop_name
        source = source_of(tree)
        register = source[source.index("def register():") :]
        self.assertIn(f"bpy.types.Scene.{name} = bpy.props.FloatProperty(", register)
        self.assertIn(f"del bpy.types.Scene.{name}", register)
        self.assertLoaded()
        self.assertTrue(hasattr(bpy.context.scene, name))
        self.assertAlmostEqual(getattr(bpy.context.scene, name), 2.5)

    def test_every_property_type_loads(self):
        tree = helpers.new_tree()
        names = []
        for idname in (
            "SNA_Node_BoolProperty",
            "SNA_Node_IntProperty",
            "SNA_Node_FloatProperty",
            "SNA_Node_FloatVectorProperty",
            "SNA_Node_StringProperty",
            "SNA_Node_EnumProperty",
            "SNA_Node_PointerProperty",
        ):
            names.append(helpers.add_node(tree, idname).prop_name)
        helpers.flush()
        self.assertLoaded()
        for name in names:
            self.assertTrue(hasattr(bpy.context.scene, name), name)

    def test_operator_property_is_an_annotation(self):
        tree = helpers.new_tree()
        op = helpers.add_node(tree, "SNA_Node_Operator")
        prop = helpers.add_node(tree, "SNA_Node_StringProperty")
        prop.register_on = "Operator"
        prop.prop_default = "hi"
        attach(op, prop)
        helpers.flush()
        source = source_of(tree)
        self.assertIn(f"    {prop.prop_name}: bpy.props.StringProperty(", source)
        self.assertNotIn(f"bpy.types.Operator.{prop.prop_name}", source)
        self.assertLoaded()
        namespace, name = op.operator_idname.split(".")
        rna = getattr(getattr(bpy.ops, namespace), name).get_rna_type()
        self.assertIn(prop.prop_name, rna.properties.keys())

    def test_update_callback_gets_update_source(self):
        tree = helpers.new_tree()
        flag = helpers.add_node(tree, "SNA_Node_BoolProperty")
        count = helpers.add_node(tree, "SNA_Node_IntProperty")
        setter = helpers.add_node(tree, "SNA_Node_SetProperty")
        pick(setter, "prop", count)
        helpers.flush()
        setter.inputs["Value"].value = 7
        helpers.link(tree, flag.outputs["On Update"], setter.inputs[0])
        helpers.link(tree, flag.outputs["Update Source"], setter.inputs["Data"])
        helpers.flush()
        source = source_of(tree)
        update = flag.update_function_name()
        self.assertIn(f"def {update}(self, context):", source)
        self.assertIn(f"self.{count.prop_name} = 7", source)
        self.assertIn(f"update={update}", source)
        self.assertLoaded()
        setattr(bpy.context.scene, flag.prop_name, True)
        self.assertEqual(getattr(bpy.context.scene, count.prop_name), 7)

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

        tree = helpers.new_tree("Main")
        pointer = helpers.add_node(tree, "SNA_Node_PointerProperty")
        pointer.poll_function = function
        helpers.flush()
        source = source_of(tree)
        poll = pointer.poll_function_name()
        self.assertIn(
            f"from .{function.module_name} import {function.module_name}", source
        )
        self.assertIn(f"return bool({function.module_name}(object, self=self))", source)
        self.assertIn(f"poll={poll}", source)
        self.assertLoaded()

    # -- property groups --------------------------------------------------------

    def test_group_in_other_tree_is_imported(self):
        groups = helpers.new_tree("Groups")
        group = helpers.add_node(groups, "SNA_Node_PropertyGroup")
        member = helpers.add_node(groups, "SNA_Node_IntProperty")
        member.register_on = "PropertyGroup"
        member.prop_default = 3
        attach(group, member)

        tree = helpers.new_tree("Main")
        pointer = helpers.add_node(tree, "SNA_Node_PointerProperty")
        pointer.pointer_source = "PROPERTY_GROUP"
        pick(pointer, "group", group)
        collection = helpers.add_node(tree, "SNA_Node_CollectionProperty")
        pick(collection, "group", group)
        helpers.flush()

        source = source_of(tree)
        self.assertIn(f"from .{groups.module_name} import {group.class_name}", source)
        self.assertIn(f"type={group.class_name}", source)
        group_source = source_of(groups)
        self.assertIn(
            f"class {group.class_name}(bpy.types.PropertyGroup):", group_source
        )
        self.assertIn(f"    {member.prop_name}: bpy.props.IntProperty(", group_source)
        self.assertLoaded()

        scene = bpy.context.scene
        self.assertEqual(
            getattr(getattr(scene, pointer.prop_name), member.prop_name), 3
        )
        items = getattr(scene, collection.prop_name)
        items.add()
        self.assertEqual(len(items), 1)

    def test_nested_groups_are_defined_in_order(self):
        tree = helpers.new_tree()
        outer = helpers.add_node(tree, "SNA_Node_PropertyGroup")
        inner = helpers.add_node(tree, "SNA_Node_PropertyGroup")
        items = helpers.add_node(tree, "SNA_Node_CollectionProperty")
        items.register_on = "PropertyGroup"
        pick(items, "group", inner)
        attach(outer, items)
        helpers.flush()
        source = source_of(tree)
        self.assertLess(
            source.index(f"class {inner.class_name}("),
            source.index(f"class {outer.class_name}("),
        )
        self.assertLoaded()

    def test_missing_group_is_reported(self):
        tree = helpers.new_tree()
        op = helpers.add_node(tree, "SNA_Node_Operator")
        pointer = helpers.add_node(tree, "SNA_Node_PointerProperty")
        pointer.pointer_source = "PROPERTY_GROUP"
        pointer.register_on = "Operator"
        attach(op, pointer)
        helpers.flush()
        self.assertIn("property group", node_errors().get(pointer.id, ""))
        self.assertNotIn(op.id, node_errors())
        self.assertLoaded()

    # -- enums ------------------------------------------------------------------

    def test_enum_static_items(self):
        tree = helpers.new_tree()
        enum = helpers.add_node(tree, "SNA_Node_EnumProperty")
        enum.enum_items[1].description = "Second"
        enum.prop_default = "Option B"
        helpers.flush()
        source = source_of(tree)
        self.assertIn("('Option A', 'Option A', '')", source)
        self.assertIn("('Option B', 'Option B', 'Second')", source)
        self.assertIn("default='Option B'", source)
        self.assertLoaded()
        scene = bpy.context.scene
        self.assertEqual(getattr(scene, enum.prop_name), "Option B")
        setattr(scene, enum.prop_name, "Option A")
        self.assertEqual(getattr(scene, enum.prop_name), "Option A")

    def test_enum_dynamic_items_use_global_variable(self):
        tree = helpers.new_tree()
        variable = helpers.add_node(tree, "SNA_Node_GlobalVariable")
        enum = helpers.add_node(tree, "SNA_Node_EnumProperty")
        enum.items_mode = "DYNAMIC"
        pick(enum, "items_variable", variable)
        helpers.flush()
        source = source_of(tree)
        self.assertIn(f"def {enum.get_items_name()}(self, context):", source)
        self.assertIn(f"return {variable.getter_name()}()", source)
        self.assertNotIn(enum.id, node_errors())
        self.assertLoaded()

    # -- get / set ----------------------------------------------------------------

    def test_get_and_set_property(self):
        tree = helpers.new_tree()
        value = helpers.add_node(tree, "SNA_Node_IntProperty")
        trigger = helpers.add_node(tree, "SNA_Node_Trigger")
        # Blender mode: a pasted path, the owner is part of it
        scene = helpers.add_node(tree, "SNA_Node_GetProperty")
        scene.mode = "BLENDER"
        scene.setup_from_path("bpy.context", "scene", False)
        # Custom mode: a property of this addon, owner from the Data input
        setter = helpers.add_node(tree, "SNA_Node_SetProperty")
        pick(setter, "prop", value)
        getter = helpers.add_node(tree, "SNA_Node_GetProperty")
        pick(getter, "prop", value)
        helpers.flush()
        self.assertEqual(setter.inputs["Value"].bl_idname, "ScriptingIntegerSocket")
        setter.inputs["Value"].value = 42
        printer = helpers.add_node(tree, "SNA_Node_Print")
        helpers.link(tree, scene.outputs["Value"], setter.inputs["Data"])
        helpers.link(tree, scene.outputs["Value"], getter.inputs["Data"])
        helpers.link(tree, trigger.outputs[0], setter.inputs[0])
        helpers.link(tree, setter.outputs[0], printer.inputs[0])
        helpers.link(tree, getter.outputs["Value"], printer.inputs[1])
        helpers.flush()
        source = source_of(tree)
        self.assertIn(f"bpy.context.scene.{value.prop_name} = 42", source)
        self.assertIn(f"str(bpy.context.scene.{value.prop_name})", source)
        self.assertLoaded()
        self.assertEqual(run_trigger(trigger), {"FINISHED"})
        self.assertEqual(getattr(bpy.context.scene, value.prop_name), 42)

    def test_get_property_follows_target_type(self):
        tree = helpers.new_tree()
        op = helpers.add_node(tree, "SNA_Node_Operator")
        prop = helpers.add_node(tree, "SNA_Node_FloatProperty")
        prop.register_on = "Operator"
        attach(op, prop)
        getter = helpers.add_node(tree, "SNA_Node_GetProperty")
        pick(getter, "prop", prop)
        helpers.flush()
        self.assertEqual(getter.outputs["Value"].bl_idname, "ScriptingFloatSocket")
        self.assertTrue(getter.inputs["Data"].hide)  # operator: owner is self
        printer = helpers.add_node(tree, "SNA_Node_Print")
        helpers.link(tree, op.outputs["Execute"], printer.inputs[0])
        helpers.link(tree, getter.outputs["Value"], printer.inputs[1])
        helpers.flush()
        self.assertIn(f"self.{prop.prop_name}", source_of(tree))
        self.assertLoaded()

    def test_get_property_needs_data(self):
        tree = helpers.new_tree()
        prop = helpers.add_node(tree, "SNA_Node_BoolProperty")
        trigger = helpers.add_node(tree, "SNA_Node_Trigger")
        getter = helpers.add_node(tree, "SNA_Node_GetProperty")
        pick(getter, "prop", prop)
        printer = helpers.add_node(tree, "SNA_Node_Print")
        helpers.link(tree, trigger.outputs[0], printer.inputs[0])
        helpers.link(tree, getter.outputs["Value"], printer.inputs[1])
        helpers.flush()
        self.assertIn("Connect", node_errors().get(getter.id, ""))
        self.assertLoaded()

    # -- collections ------------------------------------------------------------

    def test_collection_nodes(self):
        tree = helpers.new_tree()
        group = helpers.add_node(tree, "SNA_Node_PropertyGroup")
        items = helpers.add_node(tree, "SNA_Node_CollectionProperty")
        pick(items, "group", group)
        trigger = helpers.add_node(tree, "SNA_Node_Trigger")
        get = helpers.add_node(tree, "SNA_Node_GetProperty")
        get.mode = "BLENDER"
        get.setup_from_path("bpy.context.scene", items.prop_name, False)
        add = helpers.add_node(tree, "SNA_Node_CollectionAdd")
        remove = helpers.add_node(tree, "SNA_Node_CollectionRemove")
        length = helpers.add_node(tree, "SNA_Node_CollectionLength")
        printer = helpers.add_node(tree, "SNA_Node_Print")
        helpers.flush()
        helpers.link(tree, trigger.outputs[0], add.inputs[0])
        helpers.link(tree, get.outputs["Value"], add.inputs["Collection"])
        helpers.link(tree, add.outputs[0], remove.inputs[0])
        helpers.link(tree, get.outputs["Value"], remove.inputs["Collection"])
        helpers.link(tree, remove.outputs[0], printer.inputs[0])
        helpers.link(tree, get.outputs["Value"], length.inputs[0])
        helpers.link(tree, length.outputs[0], printer.inputs[1])
        helpers.flush()
        source = source_of(tree)
        self.assertIn(f"= bpy.context.scene.{items.prop_name}.add()", source)
        self.assertIn(f"bpy.context.scene.{items.prop_name}.remove(0)", source)
        self.assertIn(f"len(bpy.context.scene.{items.prop_name})", source)
        self.assertLoaded()
        getattr(bpy.context.scene, items.prop_name).add()
        self.assertEqual(run_trigger(trigger), {"FINISHED"})
        self.assertEqual(len(getattr(bpy.context.scene, items.prop_name)), 1)

    # -- preferences --------------------------------------------------------------

    def test_preferences(self):
        tree = helpers.new_tree()
        prefs = helpers.add_node(tree, "SNA_Node_Preferences")
        prop = helpers.add_node(tree, "SNA_Node_BoolProperty")
        prop.register_on = "Preferences"
        attach(prefs, prop)
        label = helpers.add_node(tree, "SNA_Node_Label")
        helpers.link(tree, prefs.outputs["Draw"], label.inputs[0])
        helpers.flush()
        source = source_of(tree)
        self.assertIn("(bpy.types.AddonPreferences):", source)
        self.assertIn('bl_idname = __package__.rsplit(".", 1)[0]', source)
        self.assertIn(f"    {prop.prop_name}: bpy.props.BoolProperty(", source)
        self.assertIn("self.layout.label(", source)
        self.assertLoaded()


if __name__ == "__main__":
    unittest.main()
