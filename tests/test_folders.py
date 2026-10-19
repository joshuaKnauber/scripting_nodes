"""Folders of node trees and scripts (core/folders.py): packages of the
generated add-on, and the Files list showing them (node_tree/file_list.py)."""

import importlib
import os
import unittest

import bpy
import helpers

FLOAT = "ScriptingFloatSocket"


def errors():
    return helpers.sn("src.core.errors")


def folders():
    return helpers.sn("src.core.folders")


def file_list():
    return helpers.sn("src.node_tree.file_list")


def addon():
    return bpy.context.scene.sna.addon


def move(tree, folder):
    tree.folder = folder
    helpers.sn("src.core.scheduler").request_full()
    helpers.flush()


def run_trigger(trigger):
    namespace, op = trigger.operator_idname.split(".")
    return getattr(getattr(bpy.ops, namespace), op)()


class FoldersTest(unittest.TestCase):
    def setUp(self):
        helpers.reset_file()
        addon().addon_name = "Folder Test"

    def tearDown(self):
        for tree in list(bpy.data.node_groups):
            bpy.data.node_groups.remove(tree)
        addon().folders.clear()
        helpers.sn("src.core.scheduler").request_full()
        helpers.flush()

    def assertLoaded(self):
        self.assertIsNone(errors().addon_error)

    def double(self, folder=""):
        function, group_input, group_output = helpers.new_function(
            "Double", inputs=[("Value", FLOAT)], outputs=[("Result", FLOAT)]
        )
        math = helpers.add_node(function, "SNA_Node_Math")
        math.operation = "MULTIPLY"
        math.inputs["b"].value = 2
        helpers.link(function, group_input.outputs[0], math.inputs["a"])
        helpers.link(function, math.outputs["result"], group_output.inputs[0])
        move(function, folder)
        return function

    # -- the generated add-on -------------------------------------------------

    def test_a_folder_is_a_package(self):
        tree = helpers.new_tree("Main")
        helpers.add_node(tree, "SNA_Node_Trigger")
        move(tree, "UI/Panels")
        self.assertEqual(tree.module_path, "ui.panels.main")
        self.assertEqual(tree.module_file, "ui/panels/main.py")
        files = helpers.addon_files()
        self.assertIn("ui/panels/main.py", files)
        self.assertEqual(files["ui/__init__.py"], "")
        self.assertEqual(files["ui/panels/__init__.py"], "")
        self.assertNotIn("main.py", files)
        self.assertIn("from .ui.panels import main", files["__init__.py"])
        self.assertLoaded()

    def test_imports_between_folders_are_relative(self):
        function = self.double("Utilities/Math")
        tree = helpers.new_tree("Main")
        trigger = helpers.add_node(tree, "SNA_Node_Trigger")
        call = helpers.call_function(tree, function)
        call.inputs[0].value = 4
        p = helpers.add_node(tree, "SNA_Node_Print")
        helpers.link(tree, trigger.outputs[0], p.inputs[0])
        helpers.link(tree, call.outputs[0], p.inputs["text"])
        move(tree, "Operators")
        name = function.function_name
        source = helpers.tree_source(tree)
        self.assertIn(f"from ..utilities.math.double import {name}", source)
        # same folder: from the sibling module
        move(tree, "Utilities/Math")
        self.assertIn(f"from .double import {name}", helpers.tree_source(tree))
        # the function's module is in a folder, the caller at the top level
        move(tree, "")
        self.assertIn(
            f"from .utilities.math.double import {name}", helpers.tree_source(tree)
        )
        self.assertLoaded()
        self.assertEqual(run_trigger(trigger), {"FINISHED"})
        module = importlib.import_module(
            f"{addon().module_name}.{function.module_path}"
        )
        self.assertEqual(getattr(module, name)(21.0), 42.0)

    def test_moving_back_out_of_a_folder_reloads(self):
        tree = helpers.new_tree("Main")
        trigger = helpers.add_node(tree, "SNA_Node_Trigger")
        move(tree, "UI")
        self.assertLoaded()
        # __init__.py ran `from .ui import main` before: `main` is ui.main
        move(tree, "")
        self.assertLoaded()
        package = importlib.import_module(addon().module_name)
        self.assertEqual(package.main.__name__, f"{addon().module_name}.main")
        self.assertEqual(run_trigger(trigger), {"FINISHED"})

    def test_a_module_becomes_a_package_and_back(self):
        tools = helpers.new_tree("Tools")
        helpers.add_node(tools, "SNA_Node_Trigger")
        other = helpers.new_tree("Other")
        trigger = helpers.add_node(other, "SNA_Node_Trigger")
        helpers.flush()
        self.assertEqual(tools.module_file, "tools.py")
        # "tools" is the folder now, tools.py was loaded before
        move(other, "Tools")
        move(tools, "Elsewhere")
        self.assertEqual(other.module_file, "tools/other.py")
        self.assertLoaded()
        self.assertEqual(run_trigger(trigger), {"FINISHED"})
        # and a module again
        move(other, "")
        move(tools, "")
        self.assertEqual(tools.module_file, "tools.py")
        self.assertLoaded()
        package = importlib.import_module(addon().module_name)
        self.assertFalse(hasattr(package.tools, "__path__"))

    def test_folder_names_are_unique_module_names(self):
        tree = helpers.new_tree("Properties")
        other = helpers.new_tree("Tools")
        helpers.add_node(tree, "SNA_Node_Trigger")
        helpers.add_node(other, "SNA_Node_Trigger")
        move(tree, "Tools")
        # "properties" is the add-on's properties.py, "tools" the folder
        self.assertEqual(tree.module_path, "tools.properties_2")
        self.assertEqual(other.module_path, "tools_2")
        self.assertLoaded()

    def test_the_addon_package_in_a_folder(self):
        tree = helpers.new_tree("Main")
        prefs = helpers.add_node(tree, "SNA_Node_Preferences")
        prop = helpers.add_property("Verbose", "BOOLEAN", owner=prefs)
        checkbox = helpers.add_node(tree, "SNA_Node_Checkbox")
        helpers.link(tree, prefs.outputs["Draw"], checkbox.inputs[0])
        helpers.pick_property(checkbox, prop)
        move(tree, "Settings")
        source = helpers.tree_source(tree)
        self.assertIn("from .. import __package__ as base_package", source)
        self.assertIn("bl_idname = base_package", source)
        self.assertNotIn("__package__\n", source.replace("import __package__", ""))
        self.assertLoaded()
        name = addon().module_name
        module = importlib.import_module(f"{name}.{tree.module_path}")
        (preferences,) = [
            cls
            for cls in vars(module).values()
            if isinstance(cls, type) and issubclass(cls, bpy.types.AddonPreferences)
        ]
        self.assertEqual(preferences.bl_idname, name)

    def test_relative_import(self):
        relative = helpers.sn("src.core.naming").relative_import
        self.assertEqual(relative("from .a import b", ""), "from .a import b")
        self.assertEqual(relative("from .a import b", "x"), "from ..a import b")
        self.assertEqual(relative("from . import b", "x.y"), "from ... import b")
        self.assertEqual(relative("from .x.a import b", "x"), "from .a import b")
        self.assertEqual(
            relative("from .x.y import a as b", "x.y"), "from . import a as b"
        )
        self.assertEqual(relative("import os", "x"), "import os")

    # -- folders ----------------------------------------------------------------

    def test_rename_moves_the_trees(self):
        tree = helpers.new_tree("Main")
        move(tree, "UI/Panels")
        folders().add("UI/Panels")
        folders().find("UI").name = "Interface"
        self.assertEqual(tree.folder, "Interface/Panels")
        self.assertIsNotNone(folders().find("Interface/Panels"))
        self.assertIsNone(folders().find("UI"))
        # a sibling with that name: made unique
        folders().add("Other")
        folders().find("Other").name = "Interface"
        self.assertIsNotNone(folders().find("Interface 2"))
        # no separators in names
        folders().find("Interface 2").name = "A/B"
        self.assertIsNotNone(folders().find("A B"))

    def test_remove_moves_the_contents_up(self):
        top = helpers.new_tree("Top")
        deep = helpers.new_tree("Deep")
        move(top, "UI")
        move(deep, "UI/Panels")
        folders().sync()
        folders().remove("UI")
        self.assertEqual(top.folder, "")
        self.assertEqual(deep.folder, "Panels")
        self.assertEqual(folders().paths(), ["Panels"])

    def test_appended_trees_bring_their_folders(self):
        tree = helpers.new_tree("Main")
        tree.folder = "Imported/Tools"
        file_list().sync()
        self.assertIsNotNone(folders().find("Imported"))
        self.assertIsNotNone(folders().find("Imported/Tools"))

    # -- scripts ----------------------------------------------------------------

    def script(self, folder=None):
        """A script `tools.py` of the add-on with `double(x)`, in `folder`."""
        block = bpy.data.texts.new("tools.py")
        block.write("def double(x: float) -> float:\n    return x * 2\n")
        script = helpers.add_script(block)
        if folder is not None:
            script.folder = folder
        return script

    def call_script(self, tree, script):
        trigger = helpers.add_node(tree, "SNA_Node_Trigger")
        node = helpers.add_node(tree, "SNA_Node_ScriptFunction")
        node.script_id = script.id
        node.function_name = "double"
        helpers.flush()
        helpers.link(tree, trigger.outputs[0], node.inputs[0])
        helpers.flush()
        return trigger

    def test_scripts_are_in_scripts_by_default(self):
        script = self.script()
        self.assertEqual(script.folder, "Scripts")
        trigger = self.call_script(helpers.new_tree("Main"), script)
        files = helpers.addon_files()
        self.assertIn("scripts/tools.py", files)
        self.assertIn("from .scripts import tools", files["main.py"])
        self.assertLoaded()
        self.assertEqual(run_trigger(trigger), {"FINISHED"})

    def test_a_script_in_a_folder(self):
        script = self.script("UI/Helpers")
        tree = helpers.new_tree("Main")
        trigger = self.call_script(tree, script)
        files = helpers.addon_files()
        self.assertIn("ui/helpers/tools.py", files)
        self.assertNotIn("scripts/tools.py", files)
        self.assertIn("from .ui.helpers import tools", files["main.py"])
        move(tree, "UI")
        self.assertIn("from .helpers import tools", helpers.tree_source(tree))
        # at the top level
        script.folder = ""
        move(tree, "UI")
        self.assertIn("tools.py", helpers.addon_files())
        self.assertIn("from .. import tools", helpers.tree_source(tree))
        self.assertLoaded()
        self.assertEqual(run_trigger(trigger), {"FINISHED"})

    def test_folders_move_scripts_too(self):
        script = self.script("Old")
        folders().sync()
        folders().find("Old").name = "New"
        self.assertEqual(script.folder, "New")
        folders().remove("New")
        self.assertEqual(script.folder, "")

    # -- the Files list -----------------------------------------------------------

    def rows(self, filter_name=""):
        """Visible rows of the Files list in order: (depth, name)."""
        scene = bpy.context.scene
        laid_out = file_list().layout_rows(scene, filter_name)
        order = sorted(range(len(laid_out)), key=lambda i: laid_out[i][0])
        result = []
        for i in order:
            if laid_out[i][2]:
                shown = file_list().entry(scene, i)
                suffix = "/" if shown.kind == "FOLDER" else ""
                result.append((laid_out[i][1], shown.name + suffix))
        return result

    def test_list_shows_folders_first(self):
        helpers.new_tree("Zeta")
        move(helpers.new_tree("Panel"), "UI")
        move(helpers.new_tree("Menu"), "UI")
        move(helpers.new_tree("Deep"), "UI/Sub")
        self.script("UI")
        folders().add("Empty")
        file_list().sync()
        self.assertEqual(
            self.rows(),
            [
                (0, "Empty/"),
                (0, "UI/"),
                (1, "Sub/"),
                (2, "Deep"),
                (1, "Menu"),
                (1, "Panel"),
                (1, "tools.py"),
                (0, "Zeta"),
            ],
        )
        folders().find("UI").expanded = False
        self.assertEqual(self.rows(), [(0, "Empty/"), (0, "UI/"), (0, "Zeta")])
        # filtering shows matches in closed folders
        self.assertEqual(self.rows("dee"), [(0, "UI/"), (1, "Sub/"), (2, "Deep")])

    def test_operators(self):
        bpy.ops.sna.add_folder()
        self.assertEqual(folders().paths(), ["New Folder"])
        # new files and folders go into the selected folder
        bpy.ops.sna.add_node_tree()
        tree = next(
            t for t in bpy.data.node_groups if t.bl_idname == "ScriptingNodeTree"
        )
        self.assertEqual(tree.folder, "New Folder")
        bpy.ops.sna.add_script()
        self.assertEqual(addon().scripts[0].folder, "New Folder")
        bpy.ops.sna.add_folder()
        self.assertEqual(folders().paths(), ["New Folder", "New Folder/New Folder"])
        # move the selected folder to the top level
        bpy.ops.sna.move_to_folder(folder="/")
        self.assertEqual(folders().paths(), ["New Folder", "New Folder 2"])
        # select the tree, move it into the other folder
        file_list().select(bpy.context, "TREE", tree)
        bpy.ops.sna.move_to_folder(folder="New Folder 2")
        self.assertEqual(tree.folder, "New Folder 2")
        # removing a folder keeps its contents
        file_list().select(bpy.context, "FOLDER", folders().find("New Folder 2"))
        bpy.ops.sna.remove_file()
        self.assertEqual(tree.folder, "")
        self.assertEqual(folders().paths(), ["New Folder"])
        # removing a script keeps its text
        file_list().select(bpy.context, "SCRIPT", addon().scripts[0])
        bpy.ops.sna.remove_file()
        self.assertEqual(len(addon().scripts), 0)

    def test_addon_info_folder_in_a_folder(self):
        tree = helpers.new_tree("Main")
        info = helpers.add_node(tree, "SNA_Node_AddonInfo")
        trigger = helpers.add_node(tree, "SNA_Node_Trigger")
        p = helpers.add_node(tree, "SNA_Node_Print")
        helpers.link(tree, trigger.outputs[0], p.inputs[0])
        helpers.link(tree, info.outputs["folder"], p.inputs["text"])
        move(tree, "A/B")
        source = helpers.tree_source(tree)
        self.assertIn(
            "os.path.dirname(os.path.dirname(os.path.dirname(__file__)))", source
        )
        self.assertLoaded()
        path = helpers.sn("src.core.runtime").folder(addon().module_name)
        self.assertTrue(os.path.isfile(os.path.join(path, "a", "b", "main.py")))

    def test_functions_in_the_files_list(self):
        bpy.ops.sna.add_folder()
        bpy.ops.sna.new_group()  # + › Function: in the selected folder
        function = next(t for t in bpy.data.node_groups if t.is_function)
        self.assertEqual(function.folder, "New Folder")
        self.assertEqual(file_list().active(bpy.context).item, function)
        tree = helpers.new_tree("Main")
        call = helpers.call_function(tree, function)
        self.assertEqual(helpers.sn("src.core.functions").callers(function), [call])
        # deleting it: the nodes calling it ask for another one
        file_list().select(bpy.context, "TREE", function)
        bpy.ops.sna.remove_file()
        helpers.flush()
        self.assertFalse(any(t.is_function for t in bpy.data.node_groups))
        self.assertIsNone(call.node_tree)


if __name__ == "__main__":
    unittest.main()
