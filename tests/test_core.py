"""The update -> compile -> load pipeline (src/core)."""

import os
import sys
import unittest

import bpy
import helpers


def runtime():
    return helpers.sn("src.core.runtime")


def references():
    return helpers.sn("src.core.references")


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
        self.assertIn(repr("first"), source)
        self.assertIn(repr("second"), source)
        self.assertLess(source.index(repr("first")), source.index(repr("second")))

    def test_property_change_regenerates(self):
        tree, _, (p,) = trigger_print_tree("before")
        p.inputs[1].value = "after"
        helpers.flush()
        self.assertIn(repr("after"), read(module_file(tree)))
        self.assertNotIn(repr("before"), read(module_file(tree)))

    def test_emit_error_is_contained(self):
        tree, _, (p1, p2) = trigger_print_tree("a", "b")
        cls = type(p2)
        original = cls.emit

        def broken(self, ctx):
            raise ValueError("boom")

        cls.emit = broken
        try:
            helpers.sn("src.core.scheduler").request_full()
            helpers.flush()
            errors = helpers.sn("src.core.errors").node_errors
            self.assertIn("boom", errors.get(p1.id, ""))
            compile(helpers.tree_source(tree), "<tree>", "exec")
        finally:
            cls.emit = original
        helpers.sn("src.core.scheduler").request_full()
        helpers.flush()
        self.assertNotIn(p1.id, helpers.sn("src.core.errors").node_errors)

    def test_runtime_error_is_shown_on_node(self):
        tree = helpers.new_tree()
        trigger = helpers.add_node(tree, "SNA_Node_Trigger")
        var = helpers.add_node(tree, "SNA_Node_LocalVariable")
        var.data_type = "ScriptingIntegerSocket"
        p = helpers.add_node(tree, "SNA_Node_Print")
        math = helpers.add_node(tree, "SNA_Node_Math")
        math.operation = "DIVIDE"
        helpers.link(tree, trigger.outputs[0], var.inputs[0])
        helpers.link(tree, var.outputs[0], p.inputs[0])
        helpers.link(tree, var.outputs[1], math.inputs[0])
        helpers.link(tree, math.outputs[0], p.inputs[1])  # 0 / 0
        helpers.flush()
        namespace, op = trigger.operator_idname.split(".")
        with self.assertRaises(RuntimeError):
            getattr(getattr(bpy.ops, namespace), op)()
        errors = helpers.sn("src.core.errors")
        self.assertIn("ZeroDivisionError", errors.node_message(p.id) or "")

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
        self.assertIn(repr("two"), read(module_file(tree)))

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

    def test_undo_rebuilds_from_graph(self):
        tree, _, (p,) = trigger_print_tree("fresh")
        with open(module_file(tree), "w") as f:
            f.write("# stale\n")
        helpers.sn("src.handlers.events.on_undo").on_undo_redo()
        helpers.flush()
        self.assertIn(repr("fresh"), read(module_file(tree)))

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
        trigger = helpers.add_node(tree, "SNA_Node_Trigger")
        p = helpers.add_node(tree, "SNA_Node_Print")
        helpers.link(tree, trigger.outputs[0], p.inputs[0])
        helpers.link(tree, get.outputs[0], p.inputs[1])
        helpers.flush()
        # what the search field writes: the label (tree only for other trees)
        get.var = var.name
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
        self.assertEqual(get.var, "Renamed Variable")
        self.assertIn(f"{var.getter_name()}()", helpers.tree_source(tree))

    def test_cross_tree_reference_imports(self):
        vars_tree = helpers.new_tree("Vars")
        var = helpers.add_node(vars_tree, "SNA_Node_GlobalVariable")
        tree = helpers.new_tree("Main")
        get = helpers.add_node(tree, "SNA_Node_GetVariable")
        trigger = helpers.add_node(tree, "SNA_Node_Trigger")
        p = helpers.add_node(tree, "SNA_Node_Print")
        helpers.link(tree, trigger.outputs[0], p.inputs[0])
        helpers.link(tree, get.outputs[0], p.inputs[1])
        helpers.flush()
        get.var = f"{var.name} ({vars_tree.name})"
        helpers.flush()
        source = helpers.tree_source(tree)
        module = vars_tree.module_name
        getter = var.getter_name()
        self.assertIn(f"from .{module} import {getter}", source)
        self.assertIn(f"sn_print(sn_text({getter}()))", source)
        self.assertIsNone(helpers.sn("src.core.errors").addon_error)

    def test_import_cycles(self):
        cycles = helpers.sn("src.core.compiler").import_cycles
        uses = {"a": {"b"}, "b": {"c"}, "c": {"a"}, "d": {"a"}, "e": set()}
        self.assertEqual(
            cycles(uses), {"a": {"b", "c"}, "b": {"a", "c"}, "c": {"a", "b"}}
        )
        self.assertEqual(cycles({"a": {"b"}, "b": set()}), {})

    def test_trees_can_use_each_other(self):
        # A prints B's variable, B prints A's: a `from x import y` cycle
        trees, variables = [], []
        for name in ("A", "B"):
            tree = helpers.new_tree(name)
            var = helpers.add_node(tree, "SNA_Node_GlobalVariable")
            var.data_type = "ScriptingStringSocket"
            var.socket("value").value = f"value of {name}"
            trees.append(tree)
            variables.append(var)
        triggers = []
        for tree, var in zip(trees, reversed(variables)):
            get = helpers.add_node(tree, "SNA_Node_GetVariable")
            helpers.point(get, "var", var)
            trigger = helpers.add_node(tree, "SNA_Node_Trigger")
            p = helpers.add_node(tree, "SNA_Node_Print")
            helpers.link(tree, trigger.outputs[0], p.inputs[0])
            helpers.link(tree, get.outputs[0], p.inputs[1])
            triggers.append(trigger)
        helpers.flush()
        self.assertIsNone(helpers.sn("src.core.errors").addon_error)
        self.assertTrue(runtime().is_loaded(addon_settings().module_name))
        a, b = (tree.module_name for tree in trees)
        self.assertIn(f"from . import {b} as _{b}", helpers.tree_source(trees[0]))
        self.assertIn(f"from . import {a} as _{a}", helpers.tree_source(trees[1]))
        for trigger in triggers:
            namespace, op = trigger.operator_idname.split(".")
            self.assertEqual(getattr(getattr(bpy.ops, namespace), op)(), {"FINISHED"})

    def test_cross_tree_label_names_the_tree(self):
        vars_tree = helpers.new_tree("Vars")
        var = helpers.add_node(vars_tree, "SNA_Node_GlobalVariable")
        tree = helpers.new_tree("Main")
        get = helpers.add_node(tree, "SNA_Node_GetVariable")
        same = helpers.add_node(vars_tree, "SNA_Node_GetVariable")
        helpers.point(get, "var", var)
        helpers.point(same, "var", var)
        self.assertEqual(get.var, f"{var.name} (Vars)")
        self.assertEqual(same.var, var.name)

    def test_equal_labels_are_told_apart(self):
        tree = helpers.new_tree()
        a = helpers.add_node(tree, "SNA_Node_GlobalVariable")
        b = helpers.add_node(tree, "SNA_Node_GlobalVariable")
        a.label = b.label = "Count"
        get = helpers.add_node(tree, "SNA_Node_GetVariable")
        helpers.flush()
        labels = [label for label, _ in references().fields(get)["var"].choices(get)]
        self.assertEqual(len(set(labels)), 2)
        get.var = labels[1]
        self.assertEqual(get.resolve_reference("var"), b)
        # text that isn't a candidate keeps the current target
        get.var = "Nothing"
        self.assertEqual(get.resolve_reference("var"), b)
        get.var = ""
        self.assertIsNone(get.resolve_reference("var"))
        self.assertIsNotNone(a)

    def test_pickers_only_offer_valid_targets(self):
        tree = helpers.new_tree("A")
        other = helpers.new_tree("B")
        local = helpers.add_node(other, "SNA_Node_LocalVariable")
        global_var = helpers.add_node(other, "SNA_Node_GlobalVariable")
        get = helpers.add_node(tree, "SNA_Node_GetVariable")
        op = helpers.add_node(other, "SNA_Node_Operator")
        button = helpers.add_node(tree, "SNA_Node_Button")
        helpers.flush()

        def candidates(owner, attr):
            return references().fields(owner)[attr].candidates(owner)

        # local variables only exist in their own tree
        self.assertEqual(candidates(get, "var"), [global_var])
        self.assertEqual(candidates(button, "operator_sn"), [op])
        with self.assertRaises(ValueError):
            helpers.point(get, "var", local)

    def test_deleted_target_keeps_reference(self):
        tree, var, get = self._variable_setup()
        var_id = var.id
        tree.nodes.remove(var)
        helpers.flush()
        self.assertIsNone(get.resolve_reference("var"))
        self.assertTrue(references().is_missing(get, "var"))
        self.assertEqual(get.var, "")
        self.assertIn(get.id, helpers.sn("src.core.errors").node_errors)
        # a node with that id again (undo) restores the reference
        restored = helpers.add_node(tree, "SNA_Node_GlobalVariable")
        restored.id = var_id
        helpers.flush()
        self.assertEqual(get.resolve_reference("var"), restored)

    def test_duplicated_tree_references_its_own_nodes(self):
        tree, var, get = self._variable_setup()
        other = helpers.new_tree("Other")
        outside = helpers.add_node(other, "SNA_Node_GlobalVariable")
        get_outside = helpers.add_node(tree, "SNA_Node_GetVariable")
        helpers.point(get_outside, "var", outside)
        helpers.flush()
        copy = tree.copy()
        helpers.sn("src.core.scheduler").request_full()
        helpers.flush()
        copy_var = next(n for n in copy.nodes if n.bl_idname == var.bl_idname)
        copy_get = next(n for n in copy.nodes if n.name == get.name)
        copy_get_outside = next(n for n in copy.nodes if n.name == get_outside.name)
        self.assertEqual(copy_get.resolve_reference("var"), copy_var)
        self.assertEqual(get.resolve_reference("var"), var)
        # nodes outside the copied tree stay referenced
        self.assertEqual(copy_get_outside.resolve_reference("var"), outside)
        self.assertNotIn("sn_copied_from", copy_get.keys())

    def test_usages(self):
        tree, var, get = self._variable_setup()
        set_var = helpers.add_node(tree, "SNA_Node_SetVariable")
        helpers.point(set_var, "var", var)
        op = helpers.add_node(tree, "SNA_Node_Operator")
        button = helpers.add_node(tree, "SNA_Node_Button")
        helpers.point(button, "operator_sn", op)
        helpers.flush()
        refs = references()
        self.assertEqual({n for n, _ in refs.users(var)}, {get, set_var})
        self.assertEqual(refs.users(op), [(button, "operator_sn")])
        tools = helpers.sn("src.mcp_server.tools")
        usages = tools.find_usages(node_id=var.id)["usages"]
        self.assertEqual({u["sn_id"] for u in usages}, {get.id, set_var.id})

    # -- export -----------------------------------------------------------------

    def test_export_build(self):
        tree, _, (p,) = trigger_print_tree("shipped")
        export = helpers.sn("src.core.ops.export")
        files = export.build_files()
        source = files[f"addon/{tree.module_name}.py"]
        self.assertIn(repr("shipped"), source)
        # dev builds route print through the overlay helper, exports don't
        self.assertNotIn("sn_print", source)
        self.assertNotIn("_sn_helpers.py", files)
        self.assertIn("sn_print", read(module_file(tree)))
        for rel, src in files.items():
            if rel.endswith(".py"):
                compile(src, rel, "exec")


class FileTest(unittest.TestCase):
    def test_save_open_other_and_reopen(self):
        import tempfile

        helpers.reset_file()
        addon_settings().addon_name = "File Test"
        tree, _, _ = trigger_print_tree("saved")
        module = addon_settings().module_name
        path = os.path.join(tempfile.mkdtemp(), "file_test.blend")
        bpy.ops.wm.save_mainfile(filepath=path)

        # another file: this file's addon goes away (it doesn't persist)
        helpers.reset_file()
        self.assertFalse(runtime().is_loaded(module))

        bpy.ops.wm.open_mainfile(filepath=path)
        helpers.flush()
        self.assertEqual(addon_settings().module_name, module)
        self.assertTrue(runtime().is_loaded(module))
        tree = bpy.data.node_groups["Tree"]
        self.assertIn(repr("saved"), read(module_file(tree)))

        for t in list(bpy.data.node_groups):
            bpy.data.node_groups.remove(t)
        helpers.sn("src.core.scheduler").request_full()
        helpers.flush()
