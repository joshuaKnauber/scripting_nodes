"""Assets (core/assets.py): files and folders shipped in the add-on's
`assets` folder, and the Asset node giving their path."""

import os
import shutil
import tempfile
import zipfile

import bpy
import helpers
from flow_case import FlowTestCase, errors


def assets():
    return helpers.sn("src.core.assets")


def runtime():
    return helpers.sn("src.core.runtime")


def addon_folder():
    return runtime().folder(bpy.context.scene.sna.addon.module_name)


class AssetsTest(FlowTestCase):
    addon_name = "Asset Test"

    def setUp(self):
        super().setUp()
        self.temp = tempfile.mkdtemp()
        self.file = self.write("logo.png", b"\x89PNG fake")
        os.makedirs(os.path.join(self.temp, "textures", "wood"))
        self.write("textures/stone.jpg", b"stone")
        self.write("textures/wood/oak.jpg", b"oak")
        self.write("textures/__pycache__/x.pyc", b"skip me")

    def tearDown(self):
        bpy.context.scene.sna.addon.assets.clear()
        super().tearDown()
        shutil.rmtree(self.temp, ignore_errors=True)

    def write(self, rel, data):
        path = os.path.join(self.temp, *rel.split("/"))
        os.makedirs(os.path.dirname(path), exist_ok=True)
        with open(path, "wb") as f:
            f.write(data)
        return path

    def add_asset(self, path, name=None):
        asset = bpy.context.scene.sna.addon.assets.add()
        asset.id = helpers.sn("src.lib.ids").get_short_id()
        asset.filepath = path
        if name is not None:
            asset.name = name
        helpers.flush()
        return asset

    def asset_node(self, asset):
        node = self.add("SNA_Node_Asset")
        node.asset = asset.name
        return node

    # -- shipping ---------------------------------------------------------------

    def test_a_file_is_copied_into_assets(self):
        asset = self.add_asset(self.file)
        self.assertEqual(asset.name, "logo.png")  # from the file
        helpers.flush()
        copy = os.path.join(addon_folder(), "assets", "logo.png")
        with open(copy, "rb") as f:
            self.assertEqual(f.read(), b"\x89PNG fake")

    def test_a_folder_is_copied_with_its_contents(self):
        self.add_asset(os.path.join(self.temp, "textures"))
        files = helpers.addon_files()
        shipped = sorted(rel for rel in files if rel.startswith("assets/"))
        self.assertEqual(
            shipped, ["assets/textures/stone.jpg", "assets/textures/wood/oak.jpg"]
        )
        self.assertTrue(
            os.path.isfile(
                os.path.join(addon_folder(), "assets", "textures", "wood", "oak.jpg")
            )
        )

    def test_changes_to_the_source_are_copied(self):
        self.add_asset(self.file)
        copy = os.path.join(addon_folder(), "assets", "logo.png")
        # no copy (and no reload) while nothing changed
        self.assertFalse(runtime().apply(helpers.addon_files()))
        assets()._watch_assets()  # what it has seen
        self.write("logo.png", b"changed!")
        assets()._watch_assets()
        helpers.flush()
        with open(copy, "rb") as f:
            self.assertEqual(f.read(), b"changed!")

    def test_names_are_unique_and_renaming_renames_the_copy(self):
        first = self.add_asset(self.file)
        other = self.write("other/logo.png", b"other")
        second = self.add_asset(other)
        names = assets().file_names()
        self.assertEqual(names[first.id], "logo.png")
        self.assertEqual(names[second.id], "logo_2.png")
        second.name = "Logo.PNG"  # the same file on macOS / Windows
        self.assertEqual(assets().file_names()[second.id], "Logo_2.PNG")
        second.name = "icon.png"
        helpers.flush()
        folder = os.path.join(addon_folder(), "assets")
        self.assertEqual(sorted(os.listdir(folder)), ["icon.png", "logo.png"])

    def test_missing_source_is_an_error(self):
        asset = self.add_asset(os.path.join(self.temp, "gone.png"))
        self.assertIn("doesn't exist", errors().node_message(asset.id))
        node = self.asset_node(asset)
        self.print_value(node.outputs["path"])
        helpers.flush()
        self.assertIn("doesn't exist", errors().node_message(node.id))

    def test_export_ships_the_assets(self):
        self.add_asset(os.path.join(self.temp, "textures"))
        files = helpers.sn("src.core.ops.export").build_files()
        path = os.path.join(self.temp, "out.zip")
        helpers.sn("src.core.ops.export").write_zip(path, files)
        with zipfile.ZipFile(path) as zf:
            self.assertEqual(zf.read("assets/textures/stone.jpg"), b"stone")

    # -- the Asset node ---------------------------------------------------------

    def test_node_gives_the_path_in_the_addon(self):
        asset = self.add_asset(self.file)
        node = self.asset_node(asset)
        self.assertEqual(node.asset_id, asset.id)
        self.print_value(node.outputs["path"])
        self.assertIn(
            "os.path.join(os.path.dirname(__file__), 'assets', 'logo.png')",
            self.source(),
        )
        (path,) = self.run_trigger()
        self.assertEqual(path, os.path.join(addon_folder(), "assets", "logo.png"))
        self.assertTrue(os.path.isfile(path))

    def test_node_in_a_folder(self):
        asset = self.add_asset(self.file)
        node = self.asset_node(asset)
        self.print_value(node.outputs["path"])
        self.tree.folder = "UI/Panels"
        helpers.sn("src.core.scheduler").request_full()
        (path,) = self.run_trigger()
        self.assertEqual(path, os.path.join(addon_folder(), "assets", "logo.png"))

    def test_node_follows_renames_and_removal(self):
        asset = self.add_asset(self.file)
        node = self.asset_node(asset)
        self.print_value(node.outputs["path"])
        asset.name = "brand.png"
        self.assertIn("'brand.png'", self.source())
        self.assertEqual(node.asset, "brand.png")
        bpy.context.scene.sna.addon.active_asset = 0
        bpy.ops.sna.remove_asset()
        helpers.flush()
        self.assertIn("removed", errors().node_message(node.id))

    def test_relative_to_an_unsaved_file(self):
        asset = self.add_asset("//logo.png")
        self.assertIn("Save the .blend file", errors().node_message(asset.id))

    # -- MCP ----------------------------------------------------------------------

    def test_mcp_tool(self):
        from test_mcp_tools import call

        result = call("edit_assets", add=[{"file": self.file, "name": "brand.png"}])
        self.assertEqual(result["assets"], [{"name": "brand.png", "source": self.file}])
        call(
            "edit_tree",
            tree="Main",
            add=[
                {"ref": "a", "type": "SNA_Node_Asset", "props": {"asset": "brand.png"}}
            ],
        )
        node = next(n for n in self.tree.nodes if n.bl_idname == "SNA_Node_Asset")
        self.assertEqual(node.asset, "brand.png")
        self.assertEqual(call("edit_assets", remove=["brand.png"])["assets"], [])
