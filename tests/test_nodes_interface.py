"""Interface nodes and operator calls: the code they write."""

import unittest

import bpy
import helpers


def source(tree):
    """Unformatted module source (formatting may rewrap lines)."""
    return helpers.sn("src.core.compiler").compile_tree(tree, pretty=False)


def errors():
    return helpers.sn("src.core.errors")


def run(node):
    """Call the operator of a Trigger node."""
    namespace, name = node.operator_idname.split(".")
    return getattr(getattr(bpy.ops, namespace), name)()


class InterfaceNodesTest(unittest.TestCase):
    def setUp(self):
        helpers.reset_file()
        bpy.context.scene.sna.addon.addon_name = "Interface Test"

    def tearDown(self):
        for tree in list(bpy.data.node_groups):
            bpy.data.node_groups.remove(tree)
        bpy.context.scene.sna.addon.properties.clear()
        helpers.sn("src.core.scheduler").request_full()
        helpers.flush()

    def assertLoaded(self):
        self.assertIsNone(errors().addon_error)

    # -- property fields ------------------------------------------------------

    def test_checkbox_on_scene_property(self):
        tree = helpers.new_tree()
        prop = helpers.add_property("Enabled", "BOOLEAN", in_addon_group=False)
        panel = helpers.add_node(tree, "SNA_Node_Panel")
        checkbox = helpers.add_node(tree, "SNA_Node_Checkbox")
        helpers.link(tree, panel.outputs["Interface"], checkbox.inputs[0])
        helpers.pick_property(checkbox, prop)
        checkbox.toggle = True
        helpers.flush()
        # the owner defaults to the scene, connecting one is optional
        self.assertFalse(checkbox.socket("data").hide)
        self.assertIn(
            "self.layout.prop(context.scene, 'enabled', toggle=True)", source(tree)
        )
        scene = helpers.add_node(tree, "SNA_Node_BlendData")
        scene.path_root = "DATA"
        scene.path = "scenes[]"
        helpers.link(tree, scene.outputs[0], checkbox.socket("data"))
        helpers.flush()
        self.assertIn("self.layout.prop(bpy.data.scenes[0], 'enabled'", source(tree))
        self.assertLoaded()

    def test_checkbox_on_operator_property_uses_self(self):
        tree = helpers.new_tree()
        op = helpers.add_node(tree, "SNA_Node_Operator")
        op.invoke_type = "PROPS_DIALOG"
        prop = helpers.add_property("Enabled", "BOOLEAN", owner=op)
        checkbox = helpers.add_node(tree, "SNA_Node_Checkbox")
        checkbox.socket("text").value = "On"
        helpers.link(tree, op.outputs["Draw"], checkbox.inputs[0])
        helpers.pick_property(checkbox, prop)
        self.assertTrue(checkbox.socket("data").hide)
        self.assertIn("self.layout.prop(self, 'enabled', text='On')", source(tree))
        self.assertLoaded()

    def test_blender_property_path(self):
        tree = helpers.new_tree()
        panel = helpers.add_node(tree, "SNA_Node_Panel")
        field = helpers.add_node(tree, "SNA_Node_NumberField")
        helpers.link(tree, panel.outputs["Interface"], field.inputs[0])
        field.mode = "BLENDER"
        field.path = "scene.frame_end"
        helpers.flush()
        self.assertEqual(field.socket("text").bl_idname, "ScriptingStringSocket")
        self.assertIn("self.layout.prop(context.scene, 'frame_end')", source(tree))
        # the path is never trusted as code
        field.path = "scene; import os"
        helpers.flush()
        self.assertIn("Invalid data path", errors().node_message(field.id) or "")
        self.assertNotIn("import os", source(tree))

    # -- operators ------------------------------------------------------------

    def test_button_calls_sn_operator_with_arguments(self):
        tree = helpers.new_tree()
        op = helpers.add_node(tree, "SNA_Node_Operator")
        helpers.add_property("Count", "INTEGER", owner=op)
        panel = helpers.add_node(tree, "SNA_Node_Panel")
        button = helpers.add_node(tree, "SNA_Node_Button")
        helpers.link(tree, panel.outputs["Interface"], button.inputs[0])
        helpers.point(button, "operator_sn", op)
        helpers.flush()
        button.socket("arg_count").value = 5
        button.socket("label").value = "Go"
        helpers.flush()
        code = source(tree)
        self.assertIn(
            f"op = self.layout.operator({op.operator_idname!r}, text='Go')", code
        )
        self.assertIn("op.count = 5", code)
        self.assertLoaded()

    def test_button_text(self):
        tree = helpers.new_tree()
        op = helpers.add_node(tree, "SNA_Node_Operator")
        panel = helpers.add_node(tree, "SNA_Node_Panel")
        button = helpers.add_node(tree, "SNA_Node_Button")
        helpers.link(tree, panel.outputs["Interface"], button.inputs[0])
        helpers.point(button, "operator_sn", op)
        helpers.flush()
        # no label: Blender shows the operator's label
        self.assertIn(f"self.layout.operator({op.operator_idname!r})\n", source(tree))
        button.icon_only = True
        button.socket("icon").value = "ADD"
        helpers.flush()
        self.assertIn(
            f"self.layout.operator({op.operator_idname!r}, text=\"\", icon='ADD')",
            source(tree),
        )

    def test_run_blender_operator(self):
        operator_call = helpers.sn("src.nodes._operator_call")
        choice = next(
            display
            for display, idname in operator_call.blender_operator_choices()
            if idname == "mesh.primitive_cube_add"
        )

        tree = helpers.new_tree()
        trigger = helpers.add_node(tree, "SNA_Node_Trigger")
        node = helpers.add_node(tree, "SNA_Node_RunOperator")
        helpers.link(tree, trigger.outputs[0], node.inputs[0])
        node.mode = "BLENDER"
        node.operator_blender = choice
        helpers.flush()
        node.socket("arg_size").value = 3.0
        helpers.flush()
        code = source(tree)
        # properties left at their default aren't passed: the cube still
        # goes to the 3D cursor
        self.assertIn("bpy.ops.mesh.primitive_cube_add(size=3.0)", code)
        self.assertLoaded()

        objects = len(bpy.data.objects)
        self.assertEqual(run(trigger), {"FINISHED"})
        self.assertEqual(len(bpy.data.objects), objects + 1)
        self.assertAlmostEqual(bpy.context.object.dimensions.x, 3.0, places=4)

        node.exec_context = "INVOKE_DEFAULT"
        helpers.flush()
        self.assertIn(
            "bpy.ops.mesh.primitive_cube_add('INVOKE_DEFAULT', size=3.0)", source(tree)
        )

    # -- layouts --------------------------------------------------------------

    def test_layout_nesting(self):
        tree = helpers.new_tree()
        panel = helpers.add_node(tree, "SNA_Node_Panel")
        sub = helpers.add_node(tree, "SNA_Node_Subpanel")
        header = helpers.add_node(tree, "SNA_Node_Label")
        box = helpers.add_node(tree, "SNA_Node_Box")
        col = helpers.add_node(tree, "SNA_Node_Column")
        inner = helpers.add_node(tree, "SNA_Node_Label")
        after = helpers.add_node(tree, "SNA_Node_Label")
        helpers.link(tree, panel.outputs["Interface"], sub.inputs[0])
        helpers.link(tree, sub.outputs["Header"], header.inputs[0])
        helpers.link(tree, sub.outputs["Panel"], box.inputs[0])
        helpers.link(tree, box.outputs["Box"], col.inputs[0])
        helpers.link(tree, col.outputs["Column"], inner.inputs[0])
        helpers.link(tree, sub.outputs["After"], after.inputs[0])
        header.inputs[1].value = "head"
        inner.inputs[1].value = "inner"
        after.inputs[1].value = "after"
        helpers.flush()
        code = source(tree)
        expected = [
            "header, panel = self.layout.panel(",
            "header.label(text='head')",
            "if panel:",
            "box = panel.box()",
            "col = box.column()",
            "col.label(text='inner')",
            "self.layout.label(text='after')",
        ]
        positions = [code.index(line) for line in expected]
        self.assertEqual(positions, sorted(positions))
        # the body is inside the `if`, the label after the subpanel isn't
        lines = {line.strip(): line for line in code.splitlines()}
        indent = len(lines["if panel:"]) - len(lines["if panel:"].lstrip())
        box_line = lines["box = panel.box()"]
        self.assertEqual(len(box_line) - len(box_line.lstrip()), indent + 4)
        after_line = lines["self.layout.label(text='after')"]
        self.assertEqual(len(after_line) - len(after_line.lstrip()), indent)
        self.assertLoaded()

    def test_layout_reset_returns_to_panel_layout(self):
        tree = helpers.new_tree()
        panel = helpers.add_node(tree, "SNA_Node_Panel")
        row = helpers.add_node(tree, "SNA_Node_Row")
        reset = helpers.add_node(tree, "SNA_Node_LayoutReset")
        label = helpers.add_node(tree, "SNA_Node_Label")
        helpers.link(tree, panel.outputs["Interface"], row.inputs[0])
        helpers.link(tree, row.outputs["Row"], reset.inputs[0])
        helpers.link(tree, reset.outputs["Layout"], label.inputs[0])
        helpers.flush()
        self.assertIn("self.layout.label(", source(tree))
        self.assertLoaded()

    def test_menu_emits_class_and_call(self):
        tree = helpers.new_tree()
        panel = helpers.add_node(tree, "SNA_Node_Panel")
        menu = helpers.add_node(tree, "SNA_Node_Menu")
        item = helpers.add_node(tree, "SNA_Node_Label")
        helpers.link(tree, panel.outputs["Interface"], menu.inputs[0])
        helpers.link(tree, menu.outputs["Menu"], item.inputs[0])
        menu.socket("label").value = "More"
        item.inputs[1].value = "in menu"
        helpers.flush()
        code = source(tree)
        name = f"{bpy.context.scene.sna.addon.class_prefix}_MT_more"
        self.assertIn(f"class {name}(bpy.types.Menu):", code)
        self.assertIn(f"self.layout.menu({name!r}, text='More')", code)
        draw = code.index("def draw", code.index(f"class {name}"))
        self.assertLess(draw, code.index("self.layout.label(text='in menu')"))
        self.assertLoaded()
        self.assertTrue(hasattr(bpy.types, name))
