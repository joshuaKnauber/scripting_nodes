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
    # the depsgraph handler does this in the UI (not in background mode)
    sn("src.core.scheduler").request_full()
    flush()
    return tree


def new_function(name="Function", inputs=(), outputs=()):
    """A tree with a group interface. `inputs` / `outputs`: (name, socket
    idname) pairs, flow sockets included. Returns (tree, group input, group
    output)."""
    tree = new_tree(name)
    for in_out, items in (("INPUT", inputs), ("OUTPUT", outputs)):
        for item_name, idname in items:
            tree.interface.new_socket(item_name, in_out=in_out, socket_type=idname)
    group_input = add_node(tree, "NodeGroupInput", (-300, 0))
    group_output = add_node(tree, "NodeGroupOutput", (300, 0))
    flush()
    return tree, group_input, group_output


def call_function(tree, function, location=(0, 0)):
    node = add_node(tree, "SNA_Node_Group", location)
    node.node_tree = function
    flush()
    return node


def add_property(name, property_type="FLOAT", owner=None, **settings):
    """A property definition: an add-on property, or one of `owner` (a group
    property or an Operator / Preferences node). Flushes."""
    if owner is None:
        items = bpy.context.scene.sna.addon.properties
    elif hasattr(owner, "members"):
        items = owner.members
    else:
        items = owner.properties
    prop = items.add()
    prop.init(name, property_type)
    for key, value in settings.items():
        setattr(prop, key, value)
    sn("src.core.scheduler").request_full()
    flush()
    return prop


def prop(prop_id):
    """A property definition by id. Adding to a list can move its items in
    memory, so earlier Python references to them go stale: look them up."""
    return sn("src.core.properties").find(prop_id).prop


def pick_property(node, prop, attr="prop"):
    """Point the property field `attr` of `node` at `prop`."""
    setattr(node, attr + "_id", prop.id)
    if hasattr(node, "mark_dirty"):
        node.mark_dirty()
    sn("src.core.scheduler").request_full()
    flush()


def add_node(tree, idname, location=(0, 0)):
    node = tree.nodes.new(idname)
    node.location = location
    return node


def link(tree, from_socket, to_socket):
    # Blender runs NodeTree.update() for Python-made links only later (never
    # in background mode), so request the regeneration explicitly.
    new = tree.links.new(from_socket, to_socket)
    tree.update()
    return new


def flush():
    """Run all pending regeneration / compile / reload work synchronously."""
    sn("src.core.scheduler").flush()


def tree_source(tree):
    """Generated Python source of one tree module, as written to disk
    (unformatted, so substring checks don't depend on autopep8 wrapping)."""
    return sn("src.core.compiler").compile_tree(tree, pretty=False)


def addon_files():
    """All generated files of the addon as {relpath: source}."""
    return sn("src.core.compiler").compile_addon()


def node_classes():
    """Every registered Scripting Nodes node class."""
    base = sn("src.nodes.base_node").ScriptingBaseNode
    out = []

    def walk(cls):
        for sub in cls.__subclasses__():
            if issubclass(sub, bpy.types.Node) and getattr(sub, "is_registered", False):
                out.append(sub)
            walk(sub)

    walk(base)
    return sorted(set(out), key=lambda c: c.bl_idname)
