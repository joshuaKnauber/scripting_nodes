"""Blender data: RNA paths, typed sockets, the Blender Data node and pasting."""

import unittest

import bpy
import helpers


def rna():
    return helpers.sn("src.blend_data.rna")


def node_errors():
    return helpers.sn("src.core.errors").node_errors


def source(tree):
    return helpers.sn("src.core.compiler").compile_tree(tree, pretty=False)


def run(trigger):
    namespace, name = trigger.operator_idname.split(".")
    return getattr(getattr(bpy.ops, namespace), name)()


class RnaTest(unittest.TestCase):
    """blend_data/rna.py on its own."""

    def test_resolve_types(self):
        steps = rna().resolve(
            rna().root_step("Context"), ["active_object", "modifiers", "[]"]
        )
        self.assertEqual((steps[0].rna_type, steps[0].collection), ("Object", False))
        self.assertEqual((steps[1].rna_type, steps[1].collection), ("Modifier", True))
        self.assertEqual((steps[2].rna_type, steps[2].collection), ("Modifier", False))

    def test_members_of_subtypes(self):
        steps = rna().resolve(rna().root_step("Object"), ["modifiers", "[]", "width"])
        self.assertTrue(steps[-1].known)
        self.assertEqual(steps[-1].prop.type, "FLOAT")

    def test_unknown_members_are_untyped(self):
        steps = rna().resolve(rna().root_step("Object"), ["not_a_prop", "x"])
        self.assertFalse(steps[0].known)
        self.assertFalse(steps[1].known)
        # subscripting a non-collection: a custom property
        self.assertFalse(rna().resolve(rna().root_step("Object"), ["[]"])[0].known)

    def test_value_sockets(self):
        def socket(type_name, *parts):
            step = rna().resolve(rna().root_step(type_name), list(parts))[-1]
            return rna().value_spec(step, "value", "Value")

        self.assertEqual(
            socket("Scene", "render", "fps").idname, "ScriptingIntegerSocket"
        )
        location = socket("Object", "location")
        self.assertEqual(location.idname, "ScriptingVectorSocket")
        self.assertEqual(location.attrs["dimension"], "3")
        color = socket("Object", "color")
        self.assertEqual(color.idname, "ScriptingColorSocket")
        self.assertTrue(color.attrs["use_alpha"])
        kind = socket("Object", "type")
        self.assertEqual(kind.idname, "ScriptingStringSocket")
        self.assertIn("MESH", kind.attrs["enum_items_data"])
        objects = socket("BlendData", "objects")
        self.assertEqual(objects.attrs["blend_type"], "Object")
        self.assertTrue(objects.attrs["is_collection"])

    def test_paths_must_be_plain(self):
        self.assertEqual(rna().segments("objects[].name"), ["objects", "[]", "name"])
        for bad in (
            "scene; import os",
            "scene.name()",
            "objects[0]",
            "a..b",
            ".a",
            "a.",
        ):
            with self.assertRaises(ValueError):
                rna().segments(bad)

    def test_parse(self):
        parsed = rna().parse('bpy.data.objects["Cube"].modifiers[0].show_viewport')
        self.assertEqual(parsed.root, "DATA")
        self.assertEqual(
            parsed.segments, ["objects", "[]", "modifiers", "[]", "show_viewport"]
        )
        self.assertEqual(parsed.keys, ["Cube", 0])
        parsed = rna().parse("bpy.context.scene.render.fps")
        self.assertEqual(
            (parsed.root, parsed.segments), ("CONTEXT", ["scene", "render", "fps"])
        )
        parsed = rna().parse("bpy.types.SpaceView3D.show_gizmo")
        self.assertEqual((parsed.root, parsed.input_type), ("INPUT", "SpaceView3D"))
        self.assertEqual(rna().parse("bpy.data.objects['a\\'b']").keys, ["a'b"])
        for bad in (
            "bpy.ops.mesh.primitive_cube_add()",
            "bpy.context.scene.name; import os",
            "bpy.data.objects[len(x)]",
            "bpy.data.objects['a']name",
            "os.system",
        ):
            with self.assertRaises(ValueError, msg=bad):
                rna().parse(bad)

    def test_prefer_context(self):
        bpy.context.scene.name = "Main"
        parsed = rna().parse('bpy.data.scenes["Main"].render.fps')
        parsed = rna().prefer_context(parsed, bpy.context)
        self.assertEqual(
            (parsed.root, parsed.segments), ("CONTEXT", ["scene", "render", "fps"])
        )
        other = rna().parse('bpy.data.scenes["Other"].render.fps')
        self.assertEqual(rna().prefer_context(other, bpy.context).root, "DATA")

    def test_search(self):
        context = rna().root_step("Context")
        paths = [entry.path for entry in rna().search(context, "fps")]
        self.assertIn("scene.render.fps", paths)
        booleans = rna().search(
            context,
            "simplify",
            accept=lambda s: s.prop is not None and s.prop.type == "BOOLEAN",
        )
        self.assertIn("scene.render.use_simplify", [e.path for e in booleans])
        self.assertTrue(all(e.final.prop.type == "BOOLEAN" for e in booleans))

    def test_subtypes(self):
        self.assertIn("Mesh", rna().subtypes("ID"))
        self.assertIn("SpaceView3D", rna().subtypes("Space"))


class BlendDataNodeTest(unittest.TestCase):
    def setUp(self):
        helpers.reset_file()
        bpy.context.scene.sna.addon.addon_name = "Blend Data Test"
        self.tree = helpers.new_tree()
        self.trigger = helpers.add_node(self.tree, "SNA_Node_Trigger")

    def tearDown(self):
        for tree in list(bpy.data.node_groups):
            bpy.data.node_groups.remove(tree)
        helpers.sn("src.core.scheduler").request_full()
        helpers.flush()

    def add(self, path, root="CONTEXT"):
        node = helpers.add_node(self.tree, "SNA_Node_BlendData")
        node.path_root = root
        node.path = path
        return node

    def printed(self, socket):
        printer = helpers.add_node(self.tree, "SNA_Node_Print")
        helpers.link(self.tree, self.trigger.outputs[0], printer.inputs[0])
        helpers.link(self.tree, socket, printer.inputs[1])
        helpers.flush()
        return printer

    def test_output_is_typed(self):
        node = self.add("active_object")
        output = node.outputs[0]
        self.assertEqual(output.bl_idname, "ScriptingBlendDataSocket")
        self.assertEqual(output.blend_type, "Object")
        self.assertEqual(output.description, "Object")
        self.assertEqual(node.draw_label(), "Active Object")
        fps = self.add("scene.render.fps")
        self.assertEqual(fps.outputs[0].bl_idname, "ScriptingIntegerSocket")
        selected = self.add("selected_objects")
        self.assertTrue(selected.outputs[0].is_collection)
        self.assertEqual(selected.outputs[0].display_shape, "SQUARE")

    def test_types_travel_along_a_chain(self):
        obj = self.add("active_object")
        modifiers = self.add("modifiers", root="INPUT")
        first = self.add("[]", root="INPUT")
        name = self.add("name", root="INPUT")
        # linked "backwards" on purpose: syncing must follow the links
        helpers.link(self.tree, first.outputs[0], name.socket("data"))
        helpers.link(self.tree, modifiers.outputs[0], first.socket("data"))
        helpers.link(self.tree, obj.outputs[0], modifiers.socket("data"))
        helpers.flush()
        self.assertEqual(modifiers.outputs[0].blend_type, "Modifier")
        self.assertTrue(modifiers.outputs[0].is_collection)
        self.assertEqual(first.outputs[0].blend_type, "Modifier")
        self.assertFalse(first.outputs[0].is_collection)
        self.assertEqual(name.outputs[0].bl_idname, "ScriptingStringSocket")
        self.printed(name.outputs[0])
        self.assertIn(
            "sn_print(context.active_object.modifiers[0].name)", source(self.tree)
        )

    def test_keys_and_runtime(self):
        cube = bpy.data.objects.new("Cube", bpy.data.meshes.new("Cube"))
        bpy.context.scene.collection.objects.link(cube)
        cube.modifiers.new("Bevel", "BEVEL")
        node = helpers.add_node(self.tree, "SNA_Node_BlendData")
        node.paste_path('bpy.data.objects["Cube"].modifiers[0].show_viewport')
        self.assertEqual(node.path, "objects[].modifiers[].show_viewport")
        self.assertEqual(node.socket("key_0").value, "Cube")
        self.assertEqual(node.socket("key_1").value, 0)
        self.assertEqual(node.socket("key_0").name, "Object")
        self.assertEqual(node.outputs[0].bl_idname, "ScriptingBooleanSocket")
        setter = helpers.add_node(self.tree, "SNA_Node_SetProperty")
        setter.mode = "BLENDER"
        setter.paste_path('bpy.data.objects["Cube"].modifiers["Bevel"].show_viewport')
        helpers.link(self.tree, self.trigger.outputs[0], setter.inputs[0])
        self.assertEqual(setter.socket("value").bl_idname, "ScriptingBooleanSocket")
        setter.socket("value").value = False
        helpers.flush()
        code = source(self.tree)
        self.assertIn(
            "bpy.data.objects['Cube'].modifiers['Bevel'].show_viewport = False", code
        )
        self.assertIsNone(helpers.sn("src.core.errors").addon_error)
        self.assertEqual(run(self.trigger), {"FINISHED"})
        self.assertFalse(cube.modifiers["Bevel"].show_viewport)

    def test_active_item(self):
        node = self.add("active_object.modifiers[]")
        node.path_keys[0].mode = "ACTIVE"
        # the row stays, so the mode can be switched back
        self.assertIsNotNone(node.socket("key_0"))
        self.printed(node.outputs[0])
        self.assertIn("context.active_object.modifiers.active", source(self.tree))
        # bpy.data.objects has no active item
        objects = self.add("objects[]", root="DATA")
        objects.path_keys[0].mode = "ACTIVE"
        self.printed(objects.outputs[0])
        self.assertIn("no active item", node_errors().get(objects.id, ""))

    def test_cast(self):
        node = self.add("active_object.data")
        self.assertEqual(node.outputs[0].blend_type, "ID")
        node.path_cast = "Mesh"
        self.assertEqual(node.outputs[0].blend_type, "Mesh")
        node.path_cast = "NotAType"
        self.assertEqual(node.outputs[0].blend_type, "ID")

    def test_context_outside_functions_with_context(self):
        node = self.add("scene.frame_current")
        save = helpers.add_node(self.tree, "SNA_Node_OnSave")
        printer = helpers.add_node(self.tree, "SNA_Node_Print")
        helpers.link(self.tree, save.outputs[0], printer.inputs[0])
        helpers.link(self.tree, node.outputs[0], printer.inputs[1])
        helpers.flush()
        # handlers get no context argument
        self.assertIn("str(bpy.context.scene.frame_current)", source(self.tree))

    def test_blender_data_into_a_number_is_an_error(self):
        node = self.add("active_object")
        math = helpers.add_node(self.tree, "SNA_Node_Math")
        printer = self.printed(math.outputs[0])
        helpers.link(self.tree, node.outputs[0], math.inputs[0])
        helpers.flush()
        self.assertIn("can't be used as", node_errors().get(math.id, ""))
        self.assertTrue(printer)

    def test_invalid_path_never_reaches_the_code(self):
        node = self.add("scene")
        node.path = "scene; import os"
        self.printed(node.outputs[0])
        self.assertIn("Invalid data path", node_errors().get(node.id, ""))
        self.assertNotIn("import os", source(self.tree))

    def test_collection_items_keep_their_type(self):
        objects = self.add("objects", root="DATA")
        item = helpers.add_node(self.tree, "SNA_Node_CollectionGetItem")
        helpers.link(self.tree, objects.outputs[0], item.inputs["Collection"])
        helpers.flush()
        self.assertEqual(item.outputs[0].blend_type, "Object")

    def test_paste_prefers_the_context(self):
        bpy.context.scene.name = "Main"
        node = helpers.add_node(self.tree, "SNA_Node_BlendData")
        node.paste_path('bpy.data.scenes["Main"].render.fps', bpy.context)
        self.assertEqual((node.path_root, node.path), ("CONTEXT", "scene.render.fps"))
        self.assertEqual(node.outputs[0].bl_idname, "ScriptingIntegerSocket")

    def test_enum_output(self):
        node = self.add("active_object.type")
        self.assertEqual(node.outputs[0].bl_idname, "ScriptingStringSocket")
        self.assertIn("MESH", node.outputs[0].enum_items_data)


class ExplorerTest(unittest.TestCase):
    """blend_data/explorer.py: locations and live data."""

    def setUp(self):
        helpers.reset_file()
        self.cube = bpy.data.objects.new("Cube", bpy.data.meshes.new("Cube"))
        bpy.context.scene.collection.objects.link(self.cube)
        bpy.context.view_layer.objects.active = self.cube
        self.cube.modifiers.new("Bevel", "BEVEL")
        self.tree = helpers.new_tree()

    def tearDown(self):
        for tree in list(bpy.data.node_groups):
            bpy.data.node_groups.remove(tree)

    def explorer(self):
        return helpers.sn("src.blend_data.explorer")

    def add(self, path, root="CONTEXT"):
        node = helpers.add_node(self.tree, "SNA_Node_BlendData")
        node.path_root = root
        node.path = path
        return node

    def test_node_location_is_live(self):
        ex = self.explorer()
        node = self.add("active_object.modifiers[]")
        node.path_keys[0].mode = "NAME"
        node.socket("key_0").value = "Bevel"
        location = ex.node_location(node)
        self.assertEqual(location.keys, [ex.Key("NAME", "Bevel")])
        self.assertEqual(
            ex.evaluate(location, bpy.context), self.cube.modifiers["Bevel"]
        )
        self.assertEqual(
            [text for text, _ in location.crumbs()],
            ["Context", "Active Object", "Modifiers", "Bevel"],
        )
        # by index, and the active item
        node.path_keys[0].mode = "INDEX"
        node.socket("key_0").value = 0
        location = ex.node_location(node)
        self.assertEqual(ex.evaluate(location, bpy.context), self.cube.modifiers[0])
        node.path_keys[0].mode = "ACTIVE"
        location = ex.node_location(node)
        self.assertEqual(ex.evaluate(location, bpy.context), self.cube.modifiers.active)

    def test_unavailable(self):
        ex = self.explorer()
        node = self.add("active_object.modifiers[]")
        node.path_keys[0].mode = "NAME"
        node.socket("key_0").value = "Nothing"
        with self.assertRaises(ex.Unavailable):
            ex.evaluate(ex.node_location(node), bpy.context)
        # a key from a link isn't known: types only
        number = helpers.add_node(self.tree, "SNA_Node_Integer")
        node.path_keys[0].mode = "INDEX"
        helpers.link(self.tree, number.outputs[0], node.socket("key_0"))
        location = ex.node_location(node)
        self.assertEqual(location.keys, [ex.Key("INDEX")])
        with self.assertRaises(ex.Unavailable):
            ex.evaluate(location, bpy.context)
        self.assertEqual(location.final_step().rna_type, "Modifier")

    def test_absolute_location_follows_the_chain(self):
        ex = self.explorer()
        active = self.add("active_object")
        bevel = self.add("modifiers[]", root="INPUT")
        bevel.path_keys[0].mode = "NAME"
        bevel.socket("key_0").value = "Bevel"
        helpers.link(self.tree, active.outputs[0], bevel.socket("data"))
        helpers.flush()
        location = ex.absolute_location(bevel)
        self.assertEqual(
            location.python(), "bpy.context.active_object.modifiers['Bevel']"
        )
        self.assertEqual(
            ex.evaluate(location, bpy.context), self.cube.modifiers["Bevel"]
        )
        # not from a Blender Data node: unknown
        unlinked = self.add("modifiers", root="INPUT")
        with self.assertRaises(ex.Unavailable):
            ex.absolute_location(unlinked)

    def test_apply_to_node(self):
        ex = self.explorer()
        active = self.add("active_object")
        chained = self.add("modifiers", root="INPUT")
        helpers.link(self.tree, active.outputs[0], chained.socket("data"))
        helpers.flush()
        # continuing from its input: stays relative, keeps the link
        width = ex.free_location("bpy.context.active_object.modifiers['Bevel'].width")
        ex.apply_to_node(chained, width)
        self.assertEqual(
            (chained.path_root, chained.path), ("INPUT", "modifiers[].width")
        )
        self.assertTrue(chained.socket("data").is_linked)
        self.assertEqual(chained.socket("key_0").value, "Bevel")
        # somewhere else: starts there, the link goes
        frame = ex.free_location("bpy.data.scenes['Scene'].frame_end")
        ex.apply_to_node(chained, frame)
        self.assertEqual(
            (chained.path_root, chained.path), ("DATA", "scenes[].frame_end")
        )
        self.assertFalse(chained.socket("data").is_linked)

    def test_set_node_location(self):
        ex = self.explorer()
        node = self.add("active_object")
        location = ex.node_location(node)
        target = location.extended("modifiers").extended(key=ex.Key("NAME", "Bevel"))
        ex.set_node_location(node, target.extended("width"))
        self.assertEqual(node.path, "active_object.modifiers[].width")
        self.assertEqual(node.path_keys[0].mode, "NAME")
        self.assertEqual(node.socket("key_0").value, "Bevel")
        self.assertEqual(node.outputs[0].bl_idname, "ScriptingFloatSocket")
        # back to the first segment
        ex.set_node_location(node, ex.node_location(node).truncated(1))
        self.assertEqual(node.path, "active_object")
        self.assertEqual(len(node.path_keys), 0)

    def test_free_location_round_trip(self):
        ex = self.explorer()
        for text in (
            "bpy.context",
            "bpy.data",
            "bpy.context.active_object.modifiers['Bevel']",
            "bpy.data.objects['Cube'].modifiers[0]",
            "bpy.context.active_object.modifiers.active",
        ):
            location = ex.free_location(text)
            self.assertEqual(location.python(), text)
            self.assertIsNotNone(ex.evaluate(location, bpy.context))
        self.assertEqual(ex.free_location("").root, "")
        self.assertEqual(ex.free_location("not a path").root, "")

    def test_item_keys(self):
        ex = self.explorer()
        objects = bpy.data.objects
        self.assertEqual(
            ex.item_key(objects, 0, objects[0]), ex.Key("NAME", objects[0].name)
        )
        slots = self.cube.material_slots
        if len(slots):
            # material slots are named after their material, but not found by it
            self.assertEqual(ex.item_key(slots, 0, slots[0]).mode, "INDEX")

    def test_nodes_with_paths(self):
        ex = self.explorer()
        self.assertTrue(ex.uses_paths(self.add("scene")))
        getter = helpers.add_node(self.tree, "SNA_Node_GetProperty")
        self.assertFalse(ex.uses_paths(getter))  # Custom mode
        getter.mode = "BLENDER"
        self.assertTrue(ex.uses_paths(getter))
        self.assertFalse(ex.uses_paths(helpers.add_node(self.tree, "SNA_Node_Print")))

    def test_context_members(self):
        members = self.explorer().struct_members(bpy.context, bpy.context)
        names = [identifier for identifier, _, _ in members]
        self.assertIn("scene", names)  # an RNA property of Context
        self.assertIn("active_object", names)  # a context member


if __name__ == "__main__":
    unittest.main()
