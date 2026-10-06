"""Shared helpers for the in-Blender test suite.

Everything that touches addon internals goes through this module so tests
don't break when internal paths move.
"""

import importlib
import traceback

import addon_utils
import bpy

ADDON_MODULE = "bl_ext.user_default.scripting_nodes"


def enable_addon():
    addon_utils.modules_refresh()
    errors = []
    mod = addon_utils.enable(
        ADDON_MODULE,
        default_set=True,
        handle_error=lambda e: errors.append(traceback.format_exc()),
    )
    if mod is None or errors:
        raise RuntimeError("Failed to enable addon:\n" + "\n".join(errors))
    return mod


def disable_addon():
    addon_utils.disable(ADDON_MODULE, default_set=True)


def sn(path=""):
    """Import a submodule of the addon, e.g. sn("src.core.scheduler")."""
    name = ADDON_MODULE + ("." + path if path else "")
    return importlib.import_module(name)


def reset_file():
    """Load an empty factory file so each test starts from a clean slate."""
    bpy.ops.wm.read_homefile(use_empty=True, use_factory_startup=True)
    flush()


def new_tree(name="Tree"):
    tree = bpy.data.node_groups.new(name, "ScriptingNodeTree")
    flush()
    return tree


def new_tree_for(cls):
    """A tree the node class can be added to (group-only nodes get a group tree)."""
    tree = new_tree()
    if not cls.poll(tree):
        tree.is_group = True
    return tree


def add_node(tree, idname, location=(0, 0)):
    node = tree.nodes.new(idname)
    node.location = location
    return node


def link(tree, from_socket, to_socket):
    return tree.links.new(from_socket, to_socket)


def flush():
    """Run all pending regeneration / compile / reload work synchronously."""
    sn("src.features.node_tree.code_gen.watcher").watch_changes()


def tree_source(tree):
    """Generated Python source for a single tree module."""
    return sn(
        "src.features.node_tree.code_gen.generators.node_tree"
    ).code_gen_node_tree(tree)


def addon_files(build=False):
    """All generated files of the addon as {relpath: source}."""
    raise NotImplementedError


def node_classes():
    """Every registered Scripting Nodes node class."""
    base = sn("src.features.nodes.base_node").ScriptingBaseNode
    out = []

    def walk(cls):
        for sub in cls.__subclasses__():
            if issubclass(sub, bpy.types.Node) and getattr(sub, "is_registered", False):
                out.append(sub)
            walk(sub)

    walk(base)
    return sorted(set(out), key=lambda c: c.bl_idname)
