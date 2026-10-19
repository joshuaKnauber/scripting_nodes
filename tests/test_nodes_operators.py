"""Operator node invoke types (file browser, dialogs, modal), Return, Is Key,
the modal helper nodes, UI List and File Handler. Modal operators and lists
need a window: tests/gui/operators.py."""

import bpy
import helpers
from flow_case import FlowTestCase, capture, errors


class OperatorNodesTest(FlowTestCase):
    addon_name = "Op Test"

    def operator(self, label="Load", **settings):
        node = self.add("SNA_Node_Operator")
        node.socket("label").value = label
        for name, value in settings.items():
            setattr(node, name, value)
        helpers.flush()
        return node

    def call(self, node, *args, **kwargs):
        namespace, op = node.operator_idname.split(".")
        return capture(getattr(getattr(bpy.ops, namespace), op), *args, **kwargs)

    def print_in(self, flow, socket=None, text=""):
        printer = self.add("SNA_Node_Print")
        self.link(flow, printer.inputs[0])
        if socket is not None:
            self.link(socket, printer.inputs["text"])
        else:
            printer.socket("text").value = text
        return printer

    def test_broken_node_skips_only_itself(self):
        run = self.then("SNA_Node_RunOperator")  # no operator picked
        self.print_value(self.string("after"))
        self.assertIn("'after'", self.source())
        self.assertIn("Pick an operator", errors().node_message(run.id))

    def test_open_file(self):
        node = self.operator(invoke_type="FILE_BROWSER", file_filter="*.txt;*.csv")
        self.print_in(node.outputs["execute"], node.outputs["path"])
        self.assertBuilt()
        source = self.source()
        self.assertIn('filepath: bpy.props.StringProperty(subtype="FILE_PATH"', source)
        self.assertIn(
            "filter_glob: bpy.props.StringProperty(default='*.txt;*.csv'", source
        )
        self.assertIn(
            "if self.filepath:\n            return self.execute(context)", source
        )
        lines = self.call(node, "EXEC_DEFAULT", filepath="/tmp/data.csv")
        self.assertEqual(lines, ["/tmp/data.csv"])
        # dropped files are set before invoke: no browser
        self.assertEqual(
            self.call(node, "INVOKE_DEFAULT", filepath="/tmp/b.csv"), ["/tmp/b.csv"]
        )

    def test_open_files_and_folders(self):
        files = self.operator(invoke_type="FILE_BROWSER", file_mode="OPEN_FILES")
        self.print_in(files.outputs["execute"], files.outputs["paths"])
        folder = self.operator("Pick", invoke_type="FILE_BROWSER", file_mode="FOLDER")
        self.print_in(folder.outputs["execute"], folder.outputs["path"])
        self.assertBuilt()
        lines = self.call(
            files,
            "EXEC_DEFAULT",
            directory="/tmp",
            files=[{"name": "a.txt"}, {"name": "b.txt"}],
        )
        self.assertEqual(lines, [str(["/tmp/a.txt", "/tmp/b.txt"])])
        self.assertEqual(
            self.call(folder, "EXEC_DEFAULT", directory="/tmp/"), ["/tmp/"]
        )
        self.assertNotIn("filter_glob", self.source())  # no filter: all files

    def test_dialog_settings(self):
        self.operator(
            "Ask",
            invoke_type="CONFIRM",
            dialog_title="Delete?",
            dialog_message="This can't be undone",
            dialog_confirm_text="Delete",
        )
        self.operator("Settings", invoke_type="PROPS_DIALOG", dialog_width=500)
        self.assertBuilt()
        source = self.source()
        self.assertIn(
            "invoke_confirm(self, event, title='Delete?', "
            "message=\"This can't be undone\", confirm_text='Delete')",
            source,
        )
        self.assertIn("invoke_props_dialog(self, width=500)", source)

    def test_depends_on_cursor(self):
        self.operator(option_depends_on_cursor=True, cursor_pending="CROSSHAIR")
        self.assertBuilt()
        source = self.source()
        self.assertIn("'DEPENDS_ON_CURSOR'", source)
        self.assertIn("bl_cursor_pending = 'CROSSHAIR'", source)

    def test_modal_structure(self):
        node = self.operator("Draw", invoke_type="MODAL", modal_timer=0.5)
        self.assertTrue(node.outputs["modal"].enabled)
        self.assertEqual(node.outputs["invoke"].name, "Start")
        key = self.add("SNA_Node_IsKey")
        self.link(node.outputs["event"], key.socket("event"))
        branch = self.add("SNA_Node_IfElse")
        self.link(node.outputs["modal"], branch.inputs[0])
        self.link(key.outputs[0], branch.socket("condition"))
        done = self.add("SNA_Node_OperatorReturn")
        self.link(branch.outputs["then"], done.inputs[0])
        header = self.add("SNA_Node_SetHeaderText")
        self.link(node.outputs["end"], header.inputs[0])
        self.assertBuilt()
        source = self.source()
        for expected in (
            "context.window_manager.modal_handler_add(self)",
            "self._timer = context.window_manager.event_timer_add(0.5, window=context.window)",
            'if event.type in {"ESC", "RIGHTMOUSE"} and event.value == "PRESS":',
            "if event.type == 'LEFTMOUSE' and event.value == 'PRESS':",
            "return {'FINISHED'}",
            "context.window_manager.event_timer_remove(self._timer)",
            "context.area.header_text_set(None)",
            "def cancel(self, context):",
        ):
            self.assertIn(expected, source)

    def test_is_key_needs_an_event(self):
        key = self.add("SNA_Node_IsKey")
        self.print_value(key.outputs[0])
        helpers.flush()
        self.assertIn("Connect an event", errors().node_message(key.id))

    def test_event_info(self):
        node = self.operator("Where", invoke_type="INVOKE")
        info = self.add("SNA_Node_EventInfo")
        self.link(node.outputs["event"], info.socket("event"))
        last = node.outputs["invoke"]
        for key in ("type", "shift", "mouse_region", "mouse_offset", "tilt"):
            printer = self.print_in(last, info.outputs[key])
            last = printer.outputs[0]
        self.assertBuilt()
        source = self.source()
        self.assertIn("(event.mouse_region_x, event.mouse_region_y)", source)
        self.assertIn("(event.mouse_x - event.mouse_prev_x, ", source)
        # running it needs a window: tests/gui/operators.py

    def test_event_info_needs_an_event(self):
        info = self.add("SNA_Node_EventInfo")
        self.print_value(info.outputs["type"])
        helpers.flush()
        self.assertIn("Connect an event", errors().node_message(info.id))

    def test_return_ends_early(self):
        node = self.operator("Early")
        cancel = self.add("SNA_Node_OperatorReturn")
        cancel.result = "CANCELLED"
        printer = self.print_in(node.outputs["execute"], text="before")
        self.link(printer.outputs[0], cancel.inputs[0])
        self.assertBuilt()
        namespace, op = node.operator_idname.split(".")
        self.assertEqual(getattr(getattr(bpy.ops, namespace), op)(), {"CANCELLED"})

    def test_ui_list(self):
        prop = helpers.add_property("Index", "INTEGER")
        panel = self.add("SNA_Node_Panel")
        ui_list = self.add("SNA_Node_UIList")
        ui_list.label = "Objects"
        self.link(panel.outputs["body"], ui_list.inputs[0])
        helpers.flush()
        self.assertIn("Connect the collection", errors().node_message(ui_list.id))
        objects = self.add("SNA_Node_BlendData")
        objects.path_root = "DATA"
        objects.path = "objects"
        helpers.flush()
        self.link(objects.outputs[0], ui_list.socket("items"))
        helpers.pick_property(ui_list, helpers.prop(prop.id))
        self.assertEqual(ui_list.outputs["item_data"].blend_type, "Object")
        label = self.add("SNA_Node_Label")
        self.link(ui_list.outputs["item"], label.inputs[0])
        self.link(ui_list.outputs["item_data"], label.socket("text"))
        self.assertBuilt()
        source = self.source()
        self.assertIn("class OP_TEST_UL_objects(bpy.types.UIList):", source)
        self.assertIn("layout.label(text=utils.as_text(item))", source)
        self.assertIn(
            "self.layout.template_list('OP_TEST_UL_objects', \"\", bpy.data, 'objects', "
            "context.scene.op_test, 'index')",
            source,
        )
        self.assertTrue(hasattr(bpy.types, "OP_TEST_UL_objects"))

    def test_ui_list_filter_function(self):
        # Is Mesh(Object) -> Boolean, picked as the list's Filter Function
        function, group_input, group_output = helpers.new_function(
            "Is Mesh",
            inputs=[("Object", "ScriptingBlendDataSocket")],
            outputs=[("Keep", "ScriptingBooleanSocket")],
        )
        check = helpers.add_node(function, "SNA_Node_PythonExpression")
        check.code = "obj.type == 'MESH'"
        helpers.flush()
        helpers.link(function, group_input.outputs[0], check.socket("name_obj"))
        helpers.link(function, check.outputs[0], group_output.inputs[0])

        prop = helpers.add_property("Index", "INTEGER")
        panel = self.add("SNA_Node_Panel")
        ui_list = self.add("SNA_Node_UIList")
        ui_list.label = "Meshes"
        self.link(panel.outputs["body"], ui_list.inputs[0])
        objects = self.add("SNA_Node_BlendData")
        objects.path_root = "DATA"
        objects.path = "objects"
        helpers.flush()
        self.link(objects.outputs[0], ui_list.socket("items"))
        helpers.pick_property(ui_list, helpers.prop(prop.id))
        ui_list.filter_function = function
        self.assertBuilt()
        source = self.source()
        self.assertIn("def filter_items(self, context, data, property):", source)
        self.assertIn("if flags[i] and not is_mesh(item):", source)

        # the list keeps meshes only, and Blender's name filter still works
        mesh = bpy.data.objects.new("Mesh", bpy.data.meshes.new("Mesh"))
        empty = bpy.data.objects.new("Empty", None)
        self.addCleanup(bpy.data.objects.remove, empty)
        self.addCleanup(bpy.data.objects.remove, mesh)
        ui_list_class = bpy.types.OP_TEST_UL_meshes

        class FakeList:
            bitflag_filter_item = 1 << 30
            filter_name = ""
            use_filter_sort_alpha = False

        fake = FakeList()
        flags, _ = ui_list_class.filter_items(fake, bpy.context, bpy.data, "objects")
        shown = {o.name for o, f in zip(bpy.data.objects, flags) if f}
        self.assertIn("Mesh", shown)
        self.assertNotIn("Empty", shown)
        fake.filter_name = "nothing like it"
        flags, _ = ui_list_class.filter_items(fake, bpy.context, bpy.data, "objects")
        self.assertFalse(any(flags))

    def test_file_handler(self):
        loader = self.operator("Load CSV", invoke_type="FILE_BROWSER")
        handler = self.add("SNA_Node_FileHandler")
        helpers.flush()
        self.assertIn("Pick an operator", errors().node_message(handler.id))
        plain = self.operator("Plain")
        choices = [n for _, n in handler.sn_references["operator"].choices(handler)]
        self.assertEqual(choices, [loader])  # only file operators
        self.assertNotIn(plain, choices)
        helpers.point(handler, "operator", loader)
        handler.socket("label").value = "CSV"
        handler.socket("extensions").value = ".csv"
        self.assertBuilt()
        cls = bpy.types.OP_TEST_FH_csv
        self.assertEqual(cls.bl_import_operator, "op_test.load_csv")
        self.assertEqual(cls.bl_file_extensions, ".csv")
        self.assertIn("context.area.type == 'VIEW_3D'", self.source())
