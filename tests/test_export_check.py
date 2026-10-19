"""core/export_check.py: what reviewers of extensions.blender.org would ask
to change, found in the export and blamed on the node that wrote it."""

import sys

import bpy
import helpers
from flow_case import FlowTestCase

sys.path.insert(0, helpers.__file__.rsplit("/", 1)[0] + "/visual/scenarios")


def export_check():
    return helpers.sn("src.core.export_check")


def messages(issues, node=None):
    return [i.message for i in issues if node is None or i.node_id == node.id]


class ExportCheckTest(FlowTestCase):
    addon_name = "Check Test"

    def setUp(self):
        super().setUp()
        addon = bpy.context.scene.sna.addon
        addon.author = "Jane Doe"
        addon.tagline = "Checks things"
        self.run_from_operator()

    def test_example_addon_is_clean(self):
        import _toolkit_demo

        helpers.reset_file()
        _toolkit_demo.build()
        self.assertEqual(export_check().run(), [])

    def test_metadata(self):
        bpy.context.scene.sna.addon.author = ""
        self.assertIn("Set an author (Metadata)", messages(export_check().run()))

    def test_blend_file_data_and_names(self):
        data = self.add("SNA_Node_BlendData")
        data.paste_path('bpy.data.objects["Cube"].location')
        self.print_value(data.outputs[0])
        helpers.flush()
        found = messages(export_check().run(), data)
        self.assertTrue(any("bpy.data.objects" in m for m in found), found)
        self.assertTrue(any("named 'Cube'" in m for m in found), found)

    def test_python_code(self):
        statement = self.then("SNA_Node_PythonStatement")
        statement.code = "import sys; sys.path.append('/tmp')"
        helpers.flush()
        issues = export_check().run()
        found = messages(issues, statement)
        self.assertIn("Changes the sys module (it's read-only)", found)
        self.assertEqual(issues[0].severity, "ERROR")

    def test_writing_into_the_addon_folder(self):
        info = self.add("SNA_Node_AddonInfo")
        join = self.add("SNA_Node_JoinPath")
        self.link(info.outputs["folder"], join.socket("first"))
        join.socket("part").value = "presets.txt"
        write = self.then("SNA_Node_WriteTextFile")
        self.link(join.outputs[0], write.socket("path"))
        helpers.flush()
        found = messages(export_check().run(), write)
        self.assertTrue(any("extension_path_user" in m for m in found), found)

    def test_network_needs_permission_and_online_access(self):
        statement = self.then("SNA_Node_PythonStatement")
        statement.code = (
            "import urllib.request; urllib.request.urlopen('https://x.org')"
        )
        helpers.flush()
        found = messages(export_check().run())
        self.assertTrue(any("Network permission" in m for m in found), found)
        self.assertTrue(any("online_access" in m for m in found), found)

    def test_export_reports_issues(self):
        import tempfile

        bpy.context.scene.sna.addon.author = ""
        path = tempfile.mktemp(suffix=".zip")
        bpy.ops.sna.export_addon(filepath=path)
        self.assertTrue(export_check().checked)
        self.assertTrue(export_check().last)

    def test_nodes_with_errors_and_triggers(self):
        """The export keeps the nodes' errors and lists them; Trigger nodes
        are only for testing."""
        errors = helpers.sn("src.core.errors")
        button = self.then("SNA_Node_RunOperator")  # no operator picked
        helpers.flush()
        message = errors.node_message(button.id)
        self.assertTrue(message)
        found = messages(export_check().run(), button)
        self.assertTrue(any("Has an error" in m for m in found), found)
        helpers.sn("src.core.ops.export").build_files()
        self.assertEqual(errors.node_message(button.id), message)

        found = messages(export_check().run())  # FlowTestCase's Trigger
        self.assertIn("1 Trigger node only for testing, not exported", found)
