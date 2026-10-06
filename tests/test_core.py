"""The update -> compile -> load pipeline (src/core)."""

import os
import sys
import unittest

import bpy
import helpers


def runtime():
    return helpers.sn("src.core.runtime")


def addon_settings():
    return bpy.context.scene.sna.addon


def trigger_print_tree(*texts, name="Tree"):
    tree = helpers.new_tree(name)
    trigger = helpers.add_node(tree, "SNA_Node_Trigger")
    prev = trigger.outputs[0]
    prints = []
    for text in texts:
        p = helpers.add_node(tree, "SNA_Node_Print")
        p.inputs[1].value = text
        helpers.link(tree, prev, p.inputs[0])
        prev = p.outputs[0]
        prints.append(p)
    helpers.flush()
    return tree, trigger, prints


def module_file(tree):
    path = runtime().folder(addon_settings().module_name)
    return os.path.join(path, "addon", tree.module_name + ".py")


def read(path):
    with open(path) as f:
        return f.read()


class CoreTest(unittest.TestCase):
    def setUp(self):
        helpers.reset_file()
        addon_settings().addon_name = "Core Test"
        helpers.flush()

    def tearDown(self):
        # don't leave generated addons loaded for the next test
        for tree in list(bpy.data.node_groups):
            bpy.data.node_groups.remove(tree)
        helpers.sn("src.core.scheduler").request_full()
        helpers.flush()

    # -- generation -----------------------------------------------------------

    def test_links_propagate_into_code(self):
        tree, _, _ = trigger_print_tree("first", "second")
        source = helpers.tree_source(tree)
        self.assertIn('"first"', source)
        self.assertIn('"second"', source)
        self.assertLess(source.index('"first"'), source.index('"second"'))

    def test_property_change_regenerates(self):
        tree, _, (p,) = trigger_print_tree("before")
        p.inputs[1].value = "after"
        helpers.flush()
        self.assertIn('"after"', read(module_file(tree)))
        self.assertNotIn('"before"', read(module_file(tree)))

    def test_generate_error_is_contained(self):
        tree, _, (p1, p2) = trigger_print_tree("a", "b")
        cls = type(p2)
        original = cls.generate

        def broken(self):
            raise ValueError("boom")

        cls.generate = broken
        try:
            helpers.sn("src.core.scheduler").request_full()
            helpers.flush()
            errors = helpers.sn("src.core.errors").node_errors
            self.assertIn("boom", errors.get(p2.id, ""))
            compile(helpers.tree_source(tree), "<tree>", "exec")
        finally:
            cls.generate = original
        helpers.sn("src.core.scheduler").request_full()
        helpers.flush()
        self.assertNotIn(p2.id, helpers.sn("src.core.errors").node_errors)

    # -- loading ----------------------------------------------------------------

    def test_addon_is_loaded_and_runs(self):
        _, trigger, _ = trigger_print_tree("hello")
        module = addon_settings().module_name
        self.assertTrue(runtime().is_loaded(module))
        namespace, op = trigger.operator_idname.split(".")
        self.assertEqual(getattr(getattr(bpy.ops, namespace), op)(), {"FINISHED"})

    def test_hot_reload_picks_up_changes(self):
        tree, trigger, (p,) = trigger_print_tree("one")
        module = addon_settings().module_name
        tree_mod = f"{module}.addon.{tree.module_name}"
        old_module = sys.modules[tree_mod]
        p.inputs[1].value = "two"
        helpers.flush()
        self.assertIsNot(sys.modules[tree_mod], old_module)
        self.assertIn('"two"', read(module_file(tree)))

    def test_syntax_error_keeps_previous_version(self):
        tree, _, _ = trigger_print_tree("ok")
        module = addon_settings().module_name
        before = read(module_file(tree))
        files = helpers.addon_files()
        files[f"addon/{tree.module_name}.py"] += "\ndef broken(:\n"
        runtime().apply(files)
        self.assertTrue(runtime().is_loaded(module))
        self.assertEqual(read(module_file(tree)), before)
        self.assertIn("syntax error", helpers.sn("src.core.errors").addon_error)

    def test_import_error_rolls_back(self):
        tree, _, _ = trigger_print_tree("ok")
        module = addon_settings().module_name
        before = read(module_file(tree))
        files = helpers.addon_files()
        files[f"addon/{tree.module_name}.py"] += "\nraise RuntimeError('nope')\n"
        runtime().apply(files)
        self.assertTrue(runtime().is_loaded(module))
        self.assertEqual(read(module_file(tree)), before)
        self.assertIn("nope", helpers.sn("src.core.errors").addon_error)

    def test_rename_removes_old_addon(self):
        trigger_print_tree("x")
        old = addon_settings().module_name
        addon_settings().addon_name = "Renamed Thing"
        helpers.flush()
        new = addon_settings().module_name
        self.assertNotEqual(old, new)
        self.assertFalse(runtime().is_loaded(old))
        self.assertFalse(os.path.exists(runtime().folder(old)))
        self.assertTrue(runtime().is_loaded(new))

    def test_foreign_folder_is_never_touched(self):
        addon_settings().addon_name = "Foreign Addon"
        path = runtime().folder(addon_settings().module_name)
        os.makedirs(path, exist_ok=True)
        with open(os.path.join(path, "__init__.py"), "w") as f:
            f.write("# my own addon\n")
        try:
            trigger_print_tree("x")
            with open(os.path.join(path, "__init__.py")) as f:
                self.assertEqual(f.read(), "# my own addon\n")
            self.assertIn("wasn't created", helpers.sn("src.core.errors").addon_error)
        finally:
            import shutil

            shutil.rmtree(path)

    def test_deleting_all_trees_unloads(self):
        tree, _, _ = trigger_print_tree("x")
        module = addon_settings().module_name
        bpy.data.node_groups.remove(tree)
        helpers.sn("src.core.scheduler").request_full()
        helpers.flush()
        self.assertFalse(runtime().is_loaded(module))
        self.assertFalse(os.path.exists(runtime().folder(module)))

    def test_unload_does_not_touch_similar_module_names(self):
        sys.modules["core_test_other"] = type(sys)("core_test_other")
        try:
            runtime().unload("core_test")
            self.assertIn("core_test_other", sys.modules)
        finally:
            del sys.modules["core_test_other"]

    # -- consistency ------------------------------------------------------------

    def test_undo_rebuilds_stale_code(self):
        tree, _, (p,) = trigger_print_tree("fresh")
        p.code_inline = "this is stale garbage"
        helpers.sn("src.handlers.events.on_undo").on_undo_redo()
        helpers.flush()
        self.assertNotIn("garbage", p.code_inline)
        self.assertIn('"fresh"', read(module_file(tree)))

    def test_duplicated_tree_gets_own_module(self):
        tree, _, _ = trigger_print_tree("x", name="Original")
        copy = tree.copy()
        helpers.sn("src.core.scheduler").request_full()
        helpers.flush()
        self.assertNotEqual(tree.id, copy.id)
        self.assertNotEqual(tree.module_name, copy.module_name)
        ids = [n.id for t in (tree, copy) for n in t.nodes]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertTrue(os.path.exists(module_file(copy)))

    def test_module_names_are_safe(self):
        addon_settings().addon_name = "Math"
        self.assertEqual(addon_settings().module_name, "math_addon")
        tree = helpers.new_tree("3D Tools")
        self.assertTrue(tree.module_name.isidentifier())

    # -- references -------------------------------------------------------------

    def _variable_setup(self):
        tree = helpers.new_tree("Vars")
        var = helpers.add_node(tree, "SNA_Node_GlobalVariable")
        get = helpers.add_node(tree, "SNA_Node_GetVariable")
        helpers.flush()
        get.var = f"{var.name} ({tree.name})"
        helpers.flush()
        return tree, var, get

    def test_reference_survives_rename(self):
        tree, var, get = self._variable_setup()
        self.assertEqual(get.resolve_reference("var"), var)
        var.name = "Renamed Variable"
        tree.name = "Renamed Tree"
        helpers.sn("src.core.scheduler").request_full()
        helpers.flush()
        self.assertEqual(get.resolve_reference("var"), var)
        self.assertEqual(get.var, "Renamed Variable (Renamed Tree)")
        self.assertEqual(get.outputs[1].code, f"get_var_{var.id}()")

    def test_old_name_references_are_migrated(self):
        tree, var, get = self._variable_setup()
        # what files saved before data version 1 contain
        get["var"] = f"{var.name} ({tree.name})"
        get["var_ref_id"] = ""
        tree.data_version = 0
        helpers.sn("src.core.scheduler").request_full()
        helpers.flush()
        self.assertEqual(get.resolve_reference("var"), var)
        self.assertNotIn("var", get.keys())
        self.assertEqual(
            tree.data_version, helpers.sn("src.core.versioning").DATA_VERSION
        )

    # -- export -----------------------------------------------------------------

    def test_export_uses_build_mode(self):
        tree, _, (p,) = trigger_print_tree("shipped")
        export = helpers.sn("src.core.ops.export")
        files = export.build_files()
        source = files[f"addon/{tree.module_name}.py"]
        self.assertIn('"shipped"', source)
        self.assertNotIn("_sn_overlay", source)
        # live code still has the dev overlay hook
        self.assertIn("_sn_overlay", p.code_inline)
        for rel, src in files.items():
            if rel.endswith(".py"):
                compile(src, rel, "exec")
