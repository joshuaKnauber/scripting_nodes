"""Add-on metadata (settings/addon.py, core/metadata.py): blender_manifest.toml
of the extension and bl_info of the live add-on."""

import os
import subprocess
import tempfile
import tomllib
import unittest

import bpy
import helpers


def errors():
    return helpers.sn("src.core.errors")


def export_files():
    return helpers.sn("src.core.compiler").compile_addon(dev=False)


class MetadataTest(unittest.TestCase):
    def setUp(self):
        helpers.reset_file()
        self.addon = bpy.context.scene.sna.addon
        self.addon.addon_name = "Meta Test"
        helpers.new_tree("Main")
        helpers.flush()

    def tearDown(self):
        for tree in list(bpy.data.node_groups):
            bpy.data.node_groups.remove(tree)
        helpers.sn("src.core.scheduler").request_full()
        helpers.flush()

    def fill(self):
        addon = self.addon
        addon.tagline = (
            'Tools for "quick" renders (beta).'  # quotes; must end alphanumeric
        )
        addon.author = "Jane Doe"
        addon.email = "jane@example.com"
        addon.version = (2, 1, 3)
        addon.website = "https://example.com/docs"
        addon.location = "View3D > Sidebar > Render"
        addon.tags = {"Render", "3D View"}
        addon.copyright = "2025-2026 Jane Doe"
        made_in = (*bpy.app.version[:2], 0)
        self.assertEqual(tuple(addon.blender_version_min), made_in)  # default
        addon.blender_version_min = (5, 0, 0)
        addon.use_blender_version_max = True
        addon.blender_version_max = (6, 0, 0)
        addon.permission_network = True
        addon.network_reason = "Downloads render presets"
        addon.permission_files = True  # no reason: the default one
        helpers.flush()

    def test_defaults(self):
        manifest = tomllib.loads(export_files()["blender_manifest.toml"])
        self.assertEqual(manifest["id"], "meta_test")
        self.assertEqual(manifest["version"], "1.0.0")
        self.assertEqual(manifest["tagline"], "Add-on created with Scripting Nodes")
        self.assertEqual(manifest["maintainer"], "Unknown")
        self.assertEqual(manifest["license"], ["SPDX:GPL-3.0-or-later"])
        for key in ("website", "tags", "copyright", "permissions"):
            self.assertNotIn(key, manifest)

    def test_manifest(self):
        self.fill()
        manifest = tomllib.loads(export_files()["blender_manifest.toml"])
        self.assertEqual(manifest["tagline"], 'Tools for "quick" renders (beta')
        self.assertEqual(manifest["maintainer"], "Jane Doe <jane@example.com>")
        self.assertEqual(manifest["version"], "2.1.3")
        self.assertEqual(manifest["website"], "https://example.com/docs")
        self.assertEqual(manifest["tags"], ["3D View", "Render"])
        self.assertEqual(manifest["license"], ["SPDX:GPL-3.0-or-later"])
        self.assertEqual(manifest["copyright"], ["2025-2026 Jane Doe"])
        self.assertEqual(manifest["blender_version_min"], "5.0.0")
        self.assertEqual(manifest["blender_version_max"], "6.0.0")
        self.assertEqual(
            manifest["permissions"],
            {"files": "Reads and writes files", "network": "Downloads render presets"},
        )

    def test_bl_info_of_the_live_addon(self):
        self.fill()
        self.assertIsNone(errors().addon_error)
        init = helpers.addon_files()["__init__.py"]
        self.assertTrue(init.startswith("# SPDX-FileCopyrightText: 2025-2026 Jane Doe"))
        self.assertIn("# SPDX-License-Identifier: GPL-3.0-or-later", init)
        import addon_utils

        module = next(
            m for m in addon_utils.modules() if m.__name__ == self.addon.module_name
        )
        info = addon_utils.module_bl_info(module)
        self.assertEqual(info["author"], "Jane Doe")
        self.assertEqual(info["description"], 'Tools for "quick" renders (beta).')
        self.assertEqual(info["version"], (2, 1, 3))
        self.assertEqual(info["blender"], (5, 0, 0))
        self.assertEqual(info["location"], "View3D > Sidebar > Render")
        self.assertEqual(info["category"], "3D View")
        self.assertEqual(info["doc_url"], "https://example.com/docs")

    def test_copyright_gets_the_year(self):
        import datetime

        self.addon.copyright = "Jane Doe"
        year = datetime.date.today().year
        self.assertEqual(self.addon.copyright, f"{year} Jane Doe")
        self.addon.copyright = "2020-2026 Jane Doe"  # given years stay
        self.assertEqual(self.addon.copyright, "2020-2026 Jane Doe")

    def test_problems(self):
        metadata = helpers.sn("src.core.metadata")
        self.addon.copyright = "26"  # a number, no name
        self.addon.use_blender_version_max = True
        self.addon.blender_version_max = (4, 0, 0)
        problems = metadata.problems(self.addon)
        self.assertEqual(len(problems), 2)
        # left out of the manifest instead of breaking it
        manifest = tomllib.loads(export_files()["blender_manifest.toml"])
        self.assertNotIn("copyright", manifest)
        self.assertNotIn("blender_version_max", manifest)
        self.addon.email = "not an email"
        self.addon.website = "example.com"
        self.addon.addon_name = ""
        problems = metadata.problems(self.addon)[:3]
        self.assertEqual(
            problems,
            [
                "Give the add-on a name (Addon Name)",
                "Email isn't an address: 'not an email'",
                "Website needs https:// and a domain",
            ],
        )
        self.addon.email = "jane@example.com"
        self.addon.website = "https://example.com/tools"
        self.assertEqual(len(metadata.problems(self.addon)), 3)

    def test_blender_accepts_the_manifest(self):
        self.fill()
        folder = os.path.join(tempfile.mkdtemp(), self.addon.module_name)
        for rel, content in export_files().items():
            path = os.path.join(folder, *rel.split("/"))
            os.makedirs(os.path.dirname(path), exist_ok=True)
            mode = "wb" if isinstance(content, bytes) else "w"
            with open(path, mode) as f:
                f.write(content)
        result = subprocess.run(
            [
                bpy.app.binary_path,
                "--factory-startup",
                "--command",
                "extension",
                "validate",
                folder,
            ],
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
