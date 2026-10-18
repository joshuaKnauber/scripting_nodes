"""Handler events, On Blender Change (bpy.msgbus) and the layout nodes and
field styles: generated code (drawing them: tests/gui/layouts.py)."""

import bpy
import helpers
from flow_case import FlowTestCase, errors, generated_helpers


class EventNodesTest(FlowTestCase):
    addon_name = "Event Test"

    def test_new_handlers(self):
        cases = [
            ("SNA_Node_OnPlayback", "Stop", "animation_playback_post"),
            ("SNA_Node_OnBake", "Cancel", "object_bake_cancel"),
            ("SNA_Node_OnComposite", "Cancel", "composite_cancel"),
            ("SNA_Node_OnImport", "After", "blend_import_post"),
            ("SNA_Node_OnLoad", "Failed", "load_post_fail"),
            ("SNA_Node_OnRenderFinish", "Frame Saved", "render_write"),
            ("SNA_Node_OnRenderStart", "Once", "render_init"),
        ]
        for idname, choice, handler in cases:
            with self.subTest(node=idname):
                self.setUp()
                node = self.add(idname)
                items = {
                    i.name: i.identifier
                    for i in node.bl_rna.properties["when"].enum_items
                }
                node.when = items[choice]
                self.assertBuilt()
                self.assertIn(f"bpy.app.handlers.{handler}.append(", self.source())
                function = getattr(bpy.app.handlers, handler)
                self.assertTrue(any(f.__name__ == f"on_{handler}" for f in function))

    def test_render_start_keeps_its_handler(self):
        """It had one handler before: saved nodes keep it."""
        node = self.add("SNA_Node_OnRenderStart")
        self.assertEqual(node.when, "render_pre")

    def watch(self, path, root="CONTEXT"):
        node = self.add("SNA_Node_OnBlenderChange")
        node.path_root = root
        node.path = path
        helpers.flush()
        return node

    def test_on_blender_change(self):
        cases = {
            "view_layer.objects.active": ("LayerObjects", "active"),
            "active_object.location": ("Object", "location"),
            "scene.render.engine": ("RenderSettings", "engine"),
            "active_object.modifiers[].width": None,  # resolved below
        }
        for path, expected in cases.items():
            with self.subTest(path=path):
                node = self.watch(path)
                struct, prop = node.watched()
                if expected:
                    self.assertEqual((struct, prop), expected)
                else:
                    self.assertEqual(prop, "width")
                    self.assertTrue(
                        issubclass(getattr(bpy.types, struct), bpy.types.Modifier)
                    )
        self.assertBuilt()
        source = self.source()
        self.assertIn(
            "utils.subscribe('LayerObjects', 'active', on_layerobjects_active_change)",
            source,
        )
        self.assertEqual(len(generated_helpers()._subscriptions), 4)

    def test_on_blender_change_needs_a_property(self):
        node = self.watch("active_object")
        self.assertIn("Blender property", errors().node_message(node.id))
        node.path = "objects"
        node.path_root = "DATA"
        helpers.flush()
        self.assertIn("Blender property", errors().node_message(node.id))

    def test_subscriptions_end_with_the_addon(self):
        self.watch("active_object.location")
        self.assertBuilt()
        module = generated_helpers()
        handler, subscriptions = module._resubscribe, module._subscriptions
        self.assertIn(handler, bpy.app.handlers.load_post)
        bpy.context.scene.sna.addon.addon_name = "Event Test 2"  # reloads
        helpers.flush()
        self.assertNotIn(handler, bpy.app.handlers.load_post)
        self.assertEqual(subscriptions, [])  # the old ones, cleared


class LayoutNodesTest(FlowTestCase):
    addon_name = "Layout Test"

    def setUp(self):
        super().setUp()
        self.panel = self.add("SNA_Node_Panel")
        self.last = self.panel.outputs["body"]

    def field(self, idname, path, style):
        node = self.then(idname)
        node.mode = "BLENDER"
        node.path = path
        node.style = style
        helpers.flush()
        return node

    def test_text_field_styles(self):
        box = self.field("SNA_Node_TextField", "scene.render.filepath", "TEXTBOX")
        box.socket("text").value = "Notes"
        box.socket("placeholder").value = "Write here"
        search = self.field("SNA_Node_TextField", "scene.camera.name", "SEARCH")
        helpers.flush()  # nothing to search yet: error on the node
        self.assertIn("Connect the collection", errors().node_message(search.id))
        objects = self.add("SNA_Node_BlendData")
        objects.path_root = "DATA"
        objects.path = "objects"
        helpers.flush()
        self.link(objects.outputs[0], search.socket("search"))
        self.assertBuilt()
        source = self.source()
        self.assertIn("self.layout.label(text='Notes')", source)
        self.assertIn(
            "utils.textbox(self.layout, context.scene.render, 'filepath', 3, 'Write here')",
            source,
        )
        self.assertIn(
            "self.layout.prop_search(context.scene.camera, 'name', bpy.data, 'objects')",
            source,
        )

    def test_enum_and_pointer_styles(self):
        icons = self.field("SNA_Node_EnumMenu", "scene.render.engine", "ICONS")
        icons.show_labels = True
        selector = self.field("SNA_Node_PointerField", "scene.world", "SELECTOR")
        selector.socket("new").value = "world.new"
        self.assertBuilt()
        source = self.source()
        self.assertIn(
            "template_icon_view(context.scene.render, 'engine', show_labels=True, scale=5.0)",
            source,
        )
        self.assertIn("template_ID(context.scene, 'world', new='world.new')", source)

    def test_layouts(self):
        split = self.then("SNA_Node_Split")
        split.socket("factor").value = 0.25
        for key, text in (("first", "Left"), ("second", "Right")):
            label = self.add("SNA_Node_Label")
            label.socket("text").value = text
            self.link(split.outputs[key], label.inputs[0])
        grid = self.then("SNA_Node_Grid")
        grid.socket("columns").value = 2
        each = self.add("SNA_Node_DrawForEach")
        self.link(grid.outputs["content"], each.inputs[0])
        objects = self.add("SNA_Node_BlendData")
        objects.path_root = "DATA"
        objects.path = "objects"
        helpers.flush()
        self.link(objects.outputs[0], each.socket("list"))
        context_data = self.add("SNA_Node_ContextData")
        self.link(each.outputs["loop"], context_data.inputs[0])
        self.link(each.outputs["item"], context_data.socket("data"))
        progress = self.then("SNA_Node_Progress")
        progress.progress_type = "RING"
        state = self.then("SNA_Node_LayoutState")
        state.operator_context = "EXEC_DEFAULT"
        self.assertBuilt()
        source = self.source()
        for expected in (
            "split = self.layout.split(factor=0.25)",
            "grid = self.layout.grid_flow(row_major=True, columns=2,",
            "for item in bpy.data.objects:",
            "grid.context_pointer_set('item', item)",
            "self.layout.progress(factor=0.5, type='RING')",
            "col = self.layout.column()",
            "col.operator_context = 'EXEC_DEFAULT'",
        ):
            self.assertIn(expected, source)

    def test_scale_with_reset_layout(self):
        # Blender applies a layout's scale to all of it, also what came before
        # and after a Reset Layout: the scale gets a layout of its own
        row = self.then("SNA_Node_Row")
        first = self.add("SNA_Node_Label")
        first.socket("text").value = "Before"
        self.link(row.outputs["content"], first.inputs[0])
        scale = self.add("SNA_Node_LayoutScale")
        scale.socket("y").value = 2.0
        self.link(first.outputs[0], scale.inputs[0])
        big = self.add("SNA_Node_Label")
        big.socket("text").value = "Big"
        self.link(scale.outputs[0], big.inputs[0])
        reset = self.add("SNA_Node_LayoutReset")
        self.link(big.outputs[0], reset.inputs[0])
        after = self.add("SNA_Node_Label")
        after.socket("text").value = "After"
        self.link(reset.outputs["reset"], after.inputs[0])
        state = self.add("SNA_Node_LayoutState")
        state.socket("alert").value = True
        self.link(after.outputs[0], state.inputs[0])
        self.assertBuilt()
        source = self.source()
        for expected in (
            "row.label(text='Before')",
            "row_2 = row.row()",  # side by side, like the row
            "row_2.scale_y = 2.0",
            "row_2.label(text='Big')",
            "self.layout.label(text='After')",
            "col = self.layout.column()",
            "col.alert = True",
        ):
            self.assertIn(expected, source)
        # unchanged settings aren't written
        for unexpected in ("scale_x", ".enabled", ".active", "self.layout.scale"):
            self.assertNotIn(unexpected, source)

    def test_operator_menu(self):
        menu = self.then("SNA_Node_OperatorMenu")
        menu.mode = "BLENDER"
        menu.operator_blender = "object.mode_set"
        menu.enum_property = "mode"
        menu.socket("label").value = "Mode"
        buttons = self.then("SNA_Node_OperatorMenu")
        buttons.mode = "BLENDER"
        buttons.operator_blender = "object.mode_set"
        buttons.enum_property = "mode"
        buttons.style = "BUTTONS"
        self.assertBuilt()
        operator_menu = helpers.sn("src.nodes.categories.interface.node_operator_menu")
        self.assertIn("mode", operator_menu.enum_properties(menu))
        source = self.source()
        self.assertIn(
            "self.layout.operator_menu_enum('object.mode_set', 'mode', text='Mode')",
            source,
        )
        self.assertIn("self.layout.operator_enum('object.mode_set', 'mode')", source)
        buttons.enum_property = "toggle"  # a boolean
        helpers.flush()
        self.assertIn("enum properties", errors().node_message(buttons.id))

    def test_menu_contents(self):
        contents = self.then("SNA_Node_MenuContents")
        contents.source = "BLENDER"
        contents.blender_menu = "Add  [VIEW3D_MT_add]"
        menu = self.add("SNA_Node_Menu")
        menu.socket("label").value = "Tools"
        custom = self.then("SNA_Node_MenuContents")
        helpers.point(custom, "menu", menu)
        self.assertBuilt()
        source = self.source()
        self.assertIn("self.layout.menu_contents('VIEW3D_MT_add')", source)
        self.assertIn("self.layout.menu_contents('LAYOUT_TEST_MT_tools')", source)

    def test_if_else_draws_in_interface_flows(self):
        """Linked after a layout, If/Else and Switch become interface nodes."""
        column = self.then("SNA_Node_Column")
        branch = self.add("SNA_Node_IfElse")
        self.assertEqual(branch.inputs[0].kind, "PROGRAM")
        self.link(column.outputs["next"], branch.inputs[0])
        label = self.add("SNA_Node_Label")
        label.socket("text").value = "Shown"
        self.link(branch.outputs["then"], label.inputs[0])
        switch = self.add("SNA_Node_Switch")
        self.link(branch.outputs["next"], switch.inputs[0])
        self.assertBuilt()
        for node in (branch, switch):
            self.assertEqual(
                {s.kind for s in node.inputs[:1] + list(node.outputs)}, {"INTERFACE"}
            )
        self.assertFalse(any(link.is_muted for link in self.tree.links))
        self.assertIn("    self.layout.label(text='Shown')", self.source())
        # unlinked, it runs code again
        self.tree.links.remove(branch.inputs[0].links[0])
        self.tree.links.remove(branch.outputs["then"].links[0])
        self.tree.links.remove(branch.outputs["next"].links[0])
        helpers.flush()
        self.assertEqual(branch.inputs[0].kind, "PROGRAM")

    def test_if_else_follows_its_outputs(self):
        """Branches linked to interface nodes first: the input becomes an
        interface socket, so it can be linked after a layout."""
        branch = self.add("SNA_Node_IfElse")
        label = self.add("SNA_Node_Label")
        self.link(branch.outputs["else"], label.inputs[0])
        helpers.flush()
        self.assertEqual(branch.inputs[0].kind, "INTERFACE")
        self.assertFalse(any(link.is_muted for link in self.tree.links))
