"""Node packages (core/node_packages.py): zips of extra nodes, installed into
the user folder, loaded as subpackages after Scripting Nodes; their folders
merge with the built-in categories."""

import os
import tempfile
import unittest
import zipfile

import bpy
import helpers

SLUGIFY = '''import bpy

from . import sn
from ._text import slug_expression


class TT_Node_Slugify(sn.ScriptingBaseNode, bpy.types.Node):
    """Lowercase text with dashes instead of spaces."""

    bl_idname = "TT_Node_Slugify"
    bl_label = "Slugify"
    sn_inputs = [sn.String("text", "Text")]
    sn_outputs = [sn.String("slug", "Slug")]

    def emit(self, ctx):
        ctx.output("slug", slug_expression(ctx.input("text")))
'''

TEXT_HELPERS = """def slug_expression(text):
    return f"{text}.lower().replace(' ', '-')"
"""

SHOUT = '''import bpy

from . import sn


class TT_Node_Shout(sn.ScriptingBaseNode, bpy.types.Node):
    bl_idname = "TT_Node_Shout"
    bl_label = "Shout"
    sn_inputs = [sn.Interface(), sn.String("text", "Text")]
    sn_outputs = [sn.Interface("next")]

    def emit(self, ctx):
        ctx.code(f"""
            {ctx.layout}.label(text={ctx.input("text")}.upper())
            {ctx.flow("next")}
        """)
'''

META = """id = "text_tools"
name = "Text Tools"
version = "1.2.0"
author = "Jane Doe"
api = 1
"""


def make_zip(files, name="text_tools.zip", folder=""):
    """A zip of {relative path: text}, optionally all inside `folder`."""
    path = os.path.join(tempfile.mkdtemp(), name)
    with zipfile.ZipFile(path, "w") as archive:
        for rel, text in files.items():
            archive.writestr(f"{folder}/{rel}" if folder else rel, text)
    return path


def registered(idname):
    return bpy.types.Node.bl_rna_get_subclass_py(idname) is not None


def packages():
    return helpers.sn("src.core.node_packages")


def reload():
    """What node_packages.reload() does on its timer."""
    helpers.disable_addon()
    helpers.enable_addon()


class NodePackagesTest(unittest.TestCase):
    def setUp(self):
        helpers.reset_file()

    def tearDown(self):
        root = packages().install_folder()
        for name in os.listdir(root):
            packages().remove(name)
        reload()

    def install_text_tools(self, **kwargs):
        zip_path = make_zip(
            {
                "nodes.toml": META,
                "text_tools/node_slugify.py": SLUGIFY,
                "text_tools/_text.py": TEXT_HELPERS,
                "interface/node_shout.py": SHOUT,
            },
            **kwargs,
        )
        package = packages().install(zip_path)
        reload()
        return package

    def test_install_writes_index_files(self):
        package = self.install_text_tools()
        self.assertEqual(package.id, "text_tools")
        root = os.path.join(packages().install_folder(), "text_tools")
        for folder in ("", "text_tools", "interface"):
            self.assertTrue(os.path.isfile(os.path.join(root, folder, "__init__.py")))
        with open(os.path.join(root, "__init__.py")) as f:
            self.assertIn("from ... import api as sn", f.read())

    def test_nodes_load_and_merge_into_categories(self):
        self.install_text_tools(folder="text_tools-main")  # a zipped folder
        loaded = packages().packages["text_tools"]
        self.assertEqual(loaded.error, "")
        self.assertEqual((loaded.name, loaded.version), ("Text Tools", "1.2.0"))
        self.assertEqual(
            sorted(cls.bl_idname for cls in loaded.nodes),
            ["TT_Node_Shout", "TT_Node_Slugify"],
        )
        categories = helpers.sn("src.nodes.categories.categories").get_node_categories()
        interface = [cls.bl_idname for cls in categories["interface"]["nodes"]]
        self.assertIn("TT_Node_Shout", interface)
        self.assertIn("SNA_Node_Label", interface)  # merged with ours
        self.assertEqual(
            [cls.bl_idname for cls in categories["text_tools"]["nodes"]],
            ["TT_Node_Slugify"],
        )

    def test_package_nodes_compile(self):
        self.install_text_tools()
        tree = helpers.new_tree()
        trigger = helpers.add_node(tree, "SNA_Node_Trigger")
        string = helpers.add_node(tree, "SNA_Node_String")
        string.value = "Hello World"
        slug = helpers.add_node(tree, "TT_Node_Slugify")
        printer = helpers.add_node(tree, "SNA_Node_Print")
        helpers.link(tree, trigger.outputs[0], printer.inputs[0])
        helpers.link(tree, string.outputs[0], slug.inputs["Text"])
        helpers.link(tree, slug.outputs["Slug"], printer.inputs["text"])
        helpers.flush()
        self.assertIn(
            "'Hello World'.lower().replace(' ', '-')", helpers.tree_source(tree)
        )
        self.assertIsNone(helpers.sn("src.core.errors").addon_error)

    def test_broken_package_doesnt_stop_scripting_nodes(self):
        broken = make_zip(
            {"broken/node_bad.py": "raise ValueError('oops')\n"}, name="broken.zip"
        )
        packages().install(broken)
        self.install_text_tools()
        loaded = packages().packages
        self.assertEqual(
            loaded["broken"].error, "ValueError: oops (node_bad.py, line 1)"
        )
        self.assertEqual(loaded["text_tools"].error, "")
        self.assertTrue(registered("SNA_Node_Print"))

    def test_rejected_zips(self):
        InstallError = packages().InstallError
        with self.assertRaisesRegex(InstallError, "newer Scripting Nodes"):
            packages().install(make_zip({"nodes.toml": "api = 99\n", "a/node.py": ""}))
        with self.assertRaisesRegex(InstallError, "Unsafe path"):
            packages().install(make_zip({"../evil.py": ""}))
        with self.assertRaisesRegex(InstallError, "no Python files"):
            packages().install(make_zip({"readme.txt": "hi"}))

    def test_remove(self):
        self.install_text_tools()
        self.assertTrue(registered("TT_Node_Slugify"))
        packages().remove("text_tools")
        reload()
        self.assertNotIn("text_tools", packages().packages)
        self.assertFalse(registered("TT_Node_Slugify"))


if __name__ == "__main__":
    unittest.main()
