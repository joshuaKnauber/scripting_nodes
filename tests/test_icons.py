"""Icons: the Icon socket, built-in icons by name, custom icons from images
shipped with the add-on, and icons of enum items."""

import os
import importlib
import sys
import tempfile
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


def builtin_value(name):
    icon = bpy.types.UILayout.bl_rna.functions["prop"].parameters["icon"]
    return icon.enum_items[name].value


class IconsTest(unittest.TestCase):
    def setUp(self):
        helpers.reset_file()
        bpy.context.scene.sna.addon.addon_name = "Icon Test"
        self.tree = helpers.new_tree("Main")
        self.panel = self.add("SNA_Node_Panel")

    def tearDown(self):
        for tree in list(bpy.data.node_groups):
            bpy.data.node_groups.remove(tree)
        for image in list(bpy.data.images):
            bpy.data.images.remove(image)
        bpy.context.scene.sna.addon.properties.clear()
        helpers.sn("src.core.scheduler").request_full()
        helpers.flush()

    def add(self, idname):
        return helpers.add_node(self.tree, idname)

    def label(self):
        label = self.add("SNA_Node_Label")
        helpers.link(self.tree, self.panel.outputs["body"], label.inputs[0])
        return label

    def image(self, packed=False):
        image = bpy.data.images.new("Logo", 4, 4)
        image.pixels = [1.0, 0.0, 0.0, 1.0] * 16
        path = os.path.join(tempfile.mkdtemp(), "logo.png")
        image.filepath_raw = path
        image.file_format = "PNG"
        image.save()
        image.source = "FILE"
        if packed:
            image.pack()
            os.remove(path)
        return image

    def assertLoaded(self):
        self.assertIsNone(errors().addon_error)

    def test_picked_icon_is_a_name(self):
        label = self.label()
        label.inputs["icon"].value = "MESH_DATA"
        helpers.flush()
        source = helpers.tree_source(self.tree)
        self.assertIn("self.layout.label(text='', icon='MESH_DATA')", source)
        self.assertLoaded()

    def test_no_icon_no_argument(self):
        self.label()
        helpers.flush()
        self.assertIn("self.layout.label(text='')", helpers.tree_source(self.tree))

    def test_unknown_icon_names_are_errors(self):
        label = self.label()
        label.inputs["icon"].value = "NOT_AN_ICON"
        helpers.flush()
        self.assertIn("NOT_AN_ICON", errors().node_message(label.id))

    def test_icon_node_is_looked_up_when_the_code_runs(self):
        label = self.label()
        icon = self.add("SNA_Node_Icon")
        icon.icon = "MESH_DATA"
        helpers.link(self.tree, icon.outputs[0], label.inputs["icon"])
        helpers.flush()
        source = helpers.tree_source(self.tree)
        self.assertIn("icon_value=sn_icon('MESH_DATA')", source)
        self.assertLoaded()
        sn_icon = generated_helpers().sn_icon
        self.assertEqual(sn_icon("MESH_DATA"), builtin_value("MESH_DATA"))
        self.assertEqual(sn_icon("NOT_AN_ICON"), 0)
        self.assertEqual(sn_icon(42), 42)

    def test_strings_convert_to_icons(self):
        label = self.label()
        text = self.add("SNA_Node_String")
        text.value = "MESH_DATA"
        helpers.link(self.tree, text.outputs[0], label.inputs["icon"])
        helpers.flush()
        self.assertIn("icon_value=sn_icon('MESH_DATA')", helpers.tree_source(self.tree))
        self.assertLoaded()

    def test_icons_arent_numbers(self):
        label = self.label()
        number = self.add("SNA_Node_Float")
        helpers.link(self.tree, number.outputs[0], label.inputs["icon"])
        helpers.flush()
        self.assertIn("Float can't be used as Icon", errors().node_message(label.id))

    def test_custom_icon_ships_the_image(self):
        for packed in (False, True):
            with self.subTest(packed=packed):
                label = self.label()
                custom = self.add("SNA_Node_CustomIcon")
                custom.image = self.image(packed)
                helpers.link(self.tree, custom.outputs[0], label.inputs["icon"])
                helpers.flush()
                files = helpers.addon_files()
                self.assertTrue(files["icons/Logo.png"].startswith(b"\x89PNG"))
                self.assertIn(
                    "icon_value=sn_custom_icon('Logo.png')",
                    helpers.tree_source(self.tree),
                )
                self.assertLoaded()
                runtime = helpers.sn("src.core.runtime")
                module = bpy.context.scene.sna.addon.module_name
                path = os.path.join(runtime.folder(module), "icons", "Logo.png")
                self.assertTrue(os.path.isfile(path))
                # icon ids only exist with a UI: check the preview loaded
                generated = generated_helpers()
                generated.sn_custom_icon("Logo.png")
                self.assertEqual(
                    tuple(generated._sn_previews["Logo.png"].image_size), (4, 4)
                )
                self.tree.nodes.remove(custom)
                self.tree.nodes.remove(label)
                bpy.data.images.remove(bpy.data.images["Logo"])
        helpers.flush()
        self.assertNotIn("icons/Logo.png", helpers.addon_files())

    def test_custom_icon_needs_an_image(self):
        label = self.label()
        custom = self.add("SNA_Node_CustomIcon")
        helpers.link(self.tree, custom.outputs[0], label.inputs["icon"])
        helpers.flush()
        self.assertIn("Pick an image", errors().node_message(custom.id))
        custom.image = bpy.data.images.new("Painted", 4, 4)
        helpers.flush()
        self.assertIn("save or pack", errors().node_message(custom.id))

    def test_every_drawing_node_takes_an_icon(self):
        for idname in (
            "SNA_Node_Label",
            "SNA_Node_Button",
            "SNA_Node_Menu",
            "SNA_Node_Checkbox",
            "SNA_Node_NumberField",
            "SNA_Node_TextField",
            "SNA_Node_VectorField",
            "SNA_Node_EnumMenu",
            "SNA_Node_PointerField",
            "SNA_Node_EnumItem",
            "SNA_Node_Panel",
        ):
            node = self.add(idname)
            self.assertEqual(
                node.socket("icon").bl_idname, "ScriptingIconSocket", idname
            )

    def test_panel_tab_icon(self):
        self.panel.socket("icon").value = "MESH_MONKEY"
        helpers.flush()
        self.assertIn("bl_icon = 'MESH_MONKEY'", helpers.tree_source(self.tree))
        self.assertLoaded()
        custom = self.add("SNA_Node_CustomIcon")
        custom.image = self.image(packed=True)
        helpers.link(self.tree, custom.outputs[0], self.panel.socket("icon"))
        helpers.flush()
        self.assertIn(
            "bl_icon_value = sn_custom_icon('Logo.png')",
            helpers.tree_source(self.tree),
        )
        self.assertLoaded()
        # only sidebars have tabs
        self.panel.panel_space_type = "PROPERTIES"
        self.panel.panel_region_type = "WINDOW"
        helpers.flush()
        self.assertFalse(self.panel.socket("icon").enabled)
        self.assertNotIn("bl_icon", helpers.tree_source(self.tree))

    def test_static_enum_items_with_icons(self):
        mode = helpers.add_property("Mode", "ENUM", enum_flag=True)
        mode.enum_items[0].icon = "MESH_DATA"
        helpers.flush()
        source = helpers.addon_files()["addon/properties.py"]
        self.assertIn("('Option A', 'Option A', '', 'MESH_DATA', 1)", source)
        self.assertIn("('Option B', 'Option B', '', 'NONE', 2)", source)
        self.assertLoaded()

    def test_enum_item_node_with_an_icon(self):
        function, _, group_output = helpers.new_function(
            "Shapes", outputs=[("Items", "ScriptingListSocket")]
        )
        create = helpers.add_node(function, "SNA_Node_CreateList")
        for name in ("Cube", "Sphere"):
            item = helpers.add_node(function, "SNA_Node_EnumItem")
            item.name_prop = name
            item.inputs["icon"].value = "MESH_CUBE"
            helpers.link(function, item.outputs[0], create.inputs[-1])
        helpers.link(function, create.outputs["list"], group_output.inputs[0])
        helpers.add_property("Shape", "ENUM", items_function=function)
        self.assertIn(
            "('CUBE', 'Cube', '', 'MESH_CUBE')", helpers.tree_source(function)
        )
        self.assertLoaded()
        settings = bpy.context.scene.icon_test
        settings.shape = "SPHERE"
        self.assertEqual(settings.shape, "SPHERE")

    def test_function_icon_input(self):
        function, group_input, _ = helpers.new_function(
            "Draw", inputs=[("Icon", "ScriptingIconSocket")]
        )
        item = next(i for i in function.interface.items_tree if i.name == "Icon")
        item.default_value = "MESH_DATA"
        call = helpers.call_function(self.tree, function)
        self.assertEqual(call.inputs[0].value, "MESH_DATA")
