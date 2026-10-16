"""File nodes, run on a temporary folder, and the `files` permission they
add to the manifest."""

import os
import tempfile
import tomllib

import bpy
import helpers
from flow_case import FlowTestCase


class FileNodesTest(FlowTestCase):
    addon_name = "File Test"

    def setUp(self):
        super().setUp()
        self.folder = tempfile.mkdtemp()

    def path(self, *parts):
        return os.path.join(self.folder, *parts)

    def test_write_read_and_list(self):
        write = self.then("SNA_Node_WriteTextFile")
        write.socket("path").value = self.path("notes", "a.txt")  # folder is created
        write.socket("text").value = "one\n"
        append = self.then("SNA_Node_WriteTextFile")
        append.append = True
        append.socket("path").value = self.path("notes", "a.txt")
        append.socket("text").value = "two"
        folder = self.then("SNA_Node_CreateFolder")
        folder.socket("path").value = self.path("notes", "sub")
        read = self.add("SNA_Node_ReadTextFile")
        read.socket("path").value = self.path("notes", "a.txt")
        self.print_value(read.outputs["lines"])
        listing = self.add("SNA_Node_ListFolder")
        listing.kind = "BOTH"
        listing.full_paths = False
        listing.socket("folder").value = self.path("notes")
        self.print_value(listing.outputs["paths"])
        files = self.add("SNA_Node_ListFolder")
        files.socket("folder").value = self.path("notes")
        files.socket("extension").value = ".TXT"
        self.print_value(files.outputs["paths"])
        missing = self.add("SNA_Node_ReadTextFile")
        missing.socket("path").value = self.path("nothing.txt")
        self.print_value(missing.outputs["text"])
        self.assertEqual(
            self.run_trigger(),
            [
                "['one', 'two']",
                "['a.txt', 'sub']",
                str([self.path("notes", "a.txt")]),
                "",
            ],
        )

    def test_paths(self):
        join = self.add("SNA_Node_JoinPath")
        join.socket("first").value = self.folder
        self.link(self.string("render.png"), join.inputs[-1])
        info = self.add("SNA_Node_PathInfo")
        self.link(join.outputs["path"], info.socket("path"))
        for key in ("file_name", "name", "extension", "exists", "is_folder"):
            self.print_value(info.outputs[key])
        self.assertEqual(
            self.run_trigger(), ["render.png", "render", ".png", "False", "False"]
        )

    def test_blend_files(self):
        library = self.path("library.blend")
        material = bpy.data.materials.new("Gold")
        material.use_fake_user = True
        bpy.data.libraries.write(library, {material, bpy.data.materials.new("Silver")})
        bpy.data.materials.remove(material)
        contents = self.add("SNA_Node_BlendFileContents")
        contents.data_type = "materials"
        contents.socket("path").value = library
        self.print_value(contents.outputs["names"])
        load = self.then("SNA_Node_LoadFromBlend")
        load.data_type = "materials"
        load.socket("path").value = library
        load.socket("names").value = "Gold"
        count = self.add("SNA_Node_ListLength")
        self.link(load.outputs["loaded"], count.inputs[0])
        self.print_value(count.outputs["length"])
        self.assertEqual(self.run_trigger(), ["['Gold', 'Silver']", "1"])
        self.assertIn("Gold", bpy.data.materials)

    def test_files_permission(self):
        compiler = helpers.sn("src.core.compiler")
        manifest = tomllib.loads(
            compiler.compile_addon(dev=False)["blender_manifest.toml"]
        )
        self.assertNotIn("permissions", manifest)
        self.run_from_operator()
        self.then("SNA_Node_CreateFolder").socket("path").value = self.folder
        self.add("SNA_Node_JoinPath")  # no file access, no permission
        self.assertBuilt()
        self.assertEqual(compiler.used_permissions, {"files"})
        manifest = tomllib.loads(
            compiler.compile_addon(dev=False)["blender_manifest.toml"]
        )
        self.assertEqual(manifest["permissions"], {"files": "Reads and writes files"})
        bpy.context.scene.sna.addon.files_reason = "Saves presets"
        manifest = tomllib.loads(
            compiler.compile_addon(dev=False)["blender_manifest.toml"]
        )
        self.assertEqual(manifest["permissions"], {"files": "Saves presets"})
