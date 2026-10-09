"""Interface nodes, operator calls and the Script node: the code they write."""

import unittest

import bpy
import helpers


def source(tree):
    """Unformatted module source (formatting may rewrap lines)."""
    return helpers.sn("src.core.compiler").compile_tree(tree, pretty=False)


def ref(node):
    """Value to assign to a reference field pointing at `node`."""
    return helpers.sn("src.core.references").display_name(node)


def errors():
    return helpers.sn("src.core.errors")


def run(node):
    """Call the operator of a Trigger node."""
    namespace, name = node.operator_idname.split(".")
    return getattr(getattr(bpy.ops, namespace), name)()


def bool_property(tree):
    # Checkbox only cares about the property's name and owner, the Integer
    # Property stands in while Boolean Property isn't available
    idname = "SNA_Node_BoolProperty"
    if not hasattr(bpy.types, idname):
        idname = "SNA_Node_IntProperty"
    return helpers.add_node(tree, idname)


class InterfaceNodesTest(unittest.TestCase):
    def setUp(self):
        helpers.reset_file()
        bpy.context.scene.sna.addon.addon_name = "Interface Test"

    def tearDown(self):
        for tree in list(bpy.data.node_groups):
            bpy.data.node_groups.remove(tree)
        helpers.sn("src.core.scheduler").request_full()
        helpers.flush()

    def assertLoaded(self):
        self.assertIsNone(errors().addon_error)

    # -- property fields ------------------------------------------------------

    def test_checkbox_on_scene_property(self):
        tree = helpers.new_tree()
        prop = bool_property(tree)
        prop.register_on = "Scene"
        panel = helpers.add_node(tree, "SNA_Node_Panel")
        checkbox = helpers.add_node(tree, "SNA_Node_Checkbox")
        scene = helpers.add_node(tree, "SNA_Node_Scene")
        helpers.link(tree, panel.outputs["Interface"], checkbox.inputs[0])
        helpers.flush()
        checkbox.prop = ref(prop)
        helpers.flush()
        # no owner connected yet
        self.assertIn("Connect", errors().node_message(checkbox.id) or "")

        helpers.link(tree, scene.outputs["Scene"], checkbox.socket("data"))
        checkbox.toggle = True
        helpers.flush()
        code = source(tree)
        self.assertIn(
            f"self.layout.prop(bpy.context.scene, {prop.prop_name!r}, toggle=True)",
            code,
        )
        self.assertFalse(checkbox.socket("data").hide)
        self.assertLoaded()

    def test_checkbox_on_operator_property_uses_self(self):
        tree = helpers.new_tree()
        prop = bool_property(tree)
        prop.register_on = "Operator"
        op = helpers.add_node(tree, "SNA_Node_Operator")
        op.invoke_type = "PROPS_DIALOG"
        helpers.flush()
        op.class_body_properties.add().prop = ref(prop)
        checkbox = helpers.add_node(tree, "SNA_Node_Checkbox")
        checkbox.socket("text").value = "Enabled"
        helpers.link(tree, op.outputs["Draw"], checkbox.inputs[0])
        checkbox.prop = ref(prop)
        helpers.flush()
        self.assertTrue(checkbox.socket("data").hide)
        code = source(tree)
        self.assertIn(
            f"self.layout.prop(self, {prop.prop_name!r}, text='Enabled')", code
        )
        self.assertLoaded()

    def test_blender_property_path(self):
        tree = helpers.new_tree()
        panel = helpers.add_node(tree, "SNA_Node_Panel")
        field = helpers.add_node(tree, "SNA_Node_NumberField")
        helpers.link(tree, panel.outputs["Interface"], field.inputs[0])
        field.mode = "BLENDER"
        field.setup_from_path("bpy.context.scene", "frame_end", False)
        helpers.flush()
        self.assertIn("self.layout.prop(bpy.context.scene, 'frame_end')", source(tree))
        # pasted text is never trusted as code
        field.setup_from_path("bpy.context.scene; import os", "frame_end", False)
        helpers.flush()
        self.assertIn("Invalid data path", errors().node_message(field.id) or "")
        self.assertNotIn("import os", source(tree))

    # -- operators ------------------------------------------------------------

    def test_button_calls_sn_operator_with_arguments(self):
        tree = helpers.new_tree()
        prop = helpers.add_node(tree, "SNA_Node_IntProperty")
        prop.register_on = "Operator"
        op = helpers.add_node(tree, "SNA_Node_Operator")
        helpers.flush()
        op.class_body_properties.add().prop = ref(prop)
        panel = helpers.add_node(tree, "SNA_Node_Panel")
        button = helpers.add_node(tree, "SNA_Node_Button")
        helpers.link(tree, panel.outputs["Interface"], button.inputs[0])
        button.operator_sn = ref(op)
        helpers.flush()
        arg = button.socket("arg_" + prop.prop_name)
        self.assertIsNotNone(arg)
        arg.value = 5
        button.socket("label").value = "Go"
        helpers.flush()
        code = source(tree)
        self.assertIn(
            f"op = self.layout.operator({op.operator_idname!r}, text='Go')", code
        )
        self.assertIn(f"op.{prop.prop_name} = 5", code)
        self.assertLoaded()

    def test_run_blender_operator(self):
        operator_call = helpers.sn("src.nodes._operator_call")
        operator_call.refresh_blender_operator_collection()
        entries = bpy.context.window_manager.sna_blender_operators
        entry = next(e for e in entries if e.bl_idname == "mesh.primitive_cube_add")

        tree = helpers.new_tree()
        trigger = helpers.add_node(tree, "SNA_Node_Trigger")
        node = helpers.add_node(tree, "SNA_Node_RunOperator")
        helpers.link(tree, trigger.outputs[0], node.inputs[0])
        node.mode = "BLENDER"
        node.operator_blender = entry.name
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
            "col = box.column(align=False, heading='')",
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

    # -- script -----------------------------------------------------------------

    def test_script_with_variables(self):
        tree = helpers.new_tree()
        trigger = helpers.add_node(tree, "SNA_Node_Trigger")
        script = helpers.add_node(tree, "SNA_Node_Script")
        scene = helpers.add_node(tree, "SNA_Node_Scene")
        p = helpers.add_node(tree, "SNA_Node_Print")
        text = bpy.data.texts.new("double.py")
        text.write("if True:\n    result = start * 2\n")
        script.text_block = text
        script.add_variable("start", "ScriptingIntegerSocket", False)
        script.add_variable("result", "ScriptingIntegerSocket", True)
        helpers.link(tree, trigger.outputs[0], script.inputs[0])
        helpers.link(tree, scene.outputs["Frame Start"], script.socket("var_start"))
        helpers.link(tree, script.outputs[0], p.inputs[0])
        helpers.link(tree, script.socket("var_result", output=True), p.inputs[1])
        helpers.flush()
        code = source(tree)
        self.assertIn("start = bpy.context.scene.frame_start", code)
        self.assertIn("        result = start * 2", code)
        self.assertIn("sn_print(str(result))", code)
        self.assertLoaded()
        self.assertEqual(run(trigger), {"FINISHED"})

        # names stay valid identifiers and unique per side
        script.add_variable("start", "ScriptingStringSocket", False)
        script.add_variable("my var", "ScriptingStringSocket", False)
        names = [v["name"] for v in script.get_variables()]
        self.assertEqual(names, ["start", "result", "start_2", "my_var"])
