import bpy
from bpy.app.handlers import persistent
from .interface.menus.rightclick import serpens_right_click
from . import bl_info
from .nodes.compiler import compile_addon, unregister_addon
from .settings.updates import check_serpens_updates
from .settings.easybpy import check_easy_bpy_install
from .settings.handle_script_changes import (
    unwatch_script_changes,
    watch_script_changes,
    update_script_nodes,
)
from .extensions.snippet_ops import load_snippets
from .msgbus import subscribe_to_name_change
from .node_tree.graphs.node_refs import clear_node_cache


def migrate_socket_data():
    """Migrate socket data from old storage (on socket) to new storage (on node).

    This handles files created before the Blender 5.0 API changes where
    bpy.props properties can no longer store IDProperties on NodeSocket.
    Old files stored values like socket["python_value"] or socket["default_value"],
    but now we store them on the parent node with a unique key.

    There are two types of old storage:
    1. Custom IDProperties on socket (accessed via socket["key"] or socket.keys())
    2. Default bpy.props storage (accessed via socket.bl_system_properties_get())
    """
    migrated_count = 0

    for node_tree in bpy.data.node_groups:
        if node_tree.bl_idname != "ScriptingNodesTree":
            continue

        for node in node_tree.nodes:
            if not getattr(node, "is_sn", False):
                continue

            # Process all sockets (inputs and outputs)
            for is_output, sockets in [(False, node.inputs), (True, node.outputs)]:
                for index, socket in enumerate(sockets):
                    if not getattr(socket, "is_sn", False):
                        continue

                    # Build the new storage key prefix
                    socket_name = socket.name
                    is_output_str = "out" if is_output else "in"
                    key_prefix = f"_socket_{is_output_str}_{index}_{socket_name}"

                    # Collect old property values from multiple sources
                    old_props = {}

                    # Method 1: Try bl_system_properties_get (Blender 5.0 versioning API)
                    # This accesses properties that used default bpy.props storage
                    try:
                        sys_props = socket.bl_system_properties_get()
                        if sys_props:
                            for key in sys_props.keys():
                                if key not in old_props:
                                    old_props[key] = sys_props[key]
                    except (AttributeError, RuntimeError, TypeError):
                        pass

                    # Method 2: Try direct dict-like access on socket keys (custom properties)
                    # This accesses IDProperties that were set with socket["key"] = value
                    try:
                        if hasattr(socket, "keys"):
                            socket_keys = list(socket.keys())
                            for key in socket_keys:
                                if key not in old_props:
                                    old_props[key] = socket[key]
                    except (RuntimeError, TypeError, KeyError):
                        pass

                    if not old_props:
                        continue

                    # Migrate python_value
                    if "python_value" in old_props:
                        new_key = key_prefix
                        if new_key not in node:
                            node[new_key] = old_props["python_value"]
                            migrated_count += 1

                    # Migrate subtype values (default_value, value_file_path, color_value, etc.)
                    subtype_values = getattr(
                        socket, "subtype_values", {"NONE": "default_value"}
                    )
                    for subtype, attr_name in subtype_values.items():
                        if attr_name in old_props:
                            new_key = f"{key_prefix}_{attr_name}"
                            if new_key not in node:
                                node[new_key] = old_props[attr_name]
                                migrated_count += 1

                    # Also check for color values stored with different keys
                    # (before they used default bpy.props storage, now they use node storage)
                    color_keys = ["color_value", "color_alpha_value", "factor_value"]
                    for color_key in color_keys:
                        if color_key in old_props:
                            new_key = f"{key_prefix}_{color_key}"
                            if new_key not in node:
                                node[new_key] = old_props[color_key]
                                migrated_count += 1

    if migrated_count > 0:
        print(
            f"Serpens: Migrated {migrated_count} socket properties to new storage format"
        )


def _get_old_property_value(item, key):
    """Try to get an old property value from various storage methods.

    Returns the value if found, None otherwise.
    """
    # Method 1: Try bl_system_properties_get (Blender 5.0 versioning API)
    try:
        sys_props = item.bl_system_properties_get()
        if sys_props and key in sys_props:
            return sys_props[key]
    except (AttributeError, RuntimeError, TypeError):
        pass

    # Method 2: Try direct dict-like access (old IDProperty storage)
    try:
        if hasattr(item, "keys") and key in item.keys():
            return item[key]
    except (RuntimeError, TypeError, KeyError, UnicodeDecodeError):
        pass

    return None


def migrate_node_ref_data():
    """Migrate node reference names from old storage to normal bpy.props storage.

    This handles files created before the Blender 5.0 API changes.
    """
    migrated_count = 0

    for node_tree in bpy.data.node_groups:
        if node_tree.bl_idname != "ScriptingNodesTree":
            continue

        for ref_collection in node_tree.node_refs:
            for ref in ref_collection.refs:
                # Skip if name is already set
                if ref.name:
                    continue

                # Try to get old name
                old_name = _get_old_property_value(ref, "_name")

                # Fallback: use node's actual name
                if not old_name:
                    try:
                        node = ref.node
                        if node:
                            old_name = node.name
                    except (RuntimeError, TypeError):
                        pass

                if old_name:
                    ref.name = old_name
                    ref.prev_name = old_name
                    migrated_count += 1

    if migrated_count > 0:
        print(f"Serpens: Migrated {migrated_count} node reference names")


def migrate_variable_data():
    """Migrate variable names from old storage to normal bpy.props storage."""
    migrated_count = 0

    for node_tree in bpy.data.node_groups:
        if node_tree.bl_idname != "ScriptingNodesTree":
            continue

        for var in node_tree.variables:
            # Skip if name is already set (not default)
            if var.name and var.name != "New Variable":
                continue

            old_name = _get_old_property_value(var, "_name")
            if old_name:
                var.name = old_name
                var.prev_name = old_name
                migrated_count += 1

    if migrated_count > 0:
        print(f"Serpens: Migrated {migrated_count} variable names")


def migrate_scene_property_groups():
    """Migrate scene-level PropertyGroup names from old storage."""
    migrated_count = 0

    for scene in bpy.data.scenes:
        if not hasattr(scene, "sn"):
            continue

        sn = scene.sn

        # Migrate property categories
        if hasattr(sn, "property_categories"):
            for cat in sn.property_categories:
                if cat.name and cat.name != "New Category":
                    continue
                old_name = _get_old_property_value(cat, "_name")
                if old_name:
                    cat.name = old_name
                    cat.prev_name = old_name
                    migrated_count += 1

        # Migrate graph categories
        if hasattr(sn, "graph_categories"):
            for cat in sn.graph_categories:
                if cat.name and cat.name != "New Category":
                    continue
                old_name = _get_old_property_value(cat, "_name")
                if old_name:
                    cat.name = old_name
                    cat.prev_name = old_name
                    migrated_count += 1

        # Migrate assets
        if hasattr(sn, "assets"):
            for asset in sn.assets:
                if asset.name and asset.name != "Asset":
                    continue
                old_name = _get_old_property_value(asset, "_name")
                if old_name:
                    asset.name = old_name
                    asset.prev_name = old_name
                    migrated_count += 1

        # Migrate properties (scene-level)
        if hasattr(sn, "properties"):
            for prop in sn.properties:
                if prop.name and prop.name != "New Property":
                    continue
                old_name = _get_old_property_value(prop, "_name")
                if old_name:
                    prop.name = old_name
                    prop.prev_name = old_name
                    migrated_count += 1

    if migrated_count > 0:
        print(f"Serpens: Migrated {migrated_count} scene property group names")


@persistent
def depsgraph_handler(dummy):
    for group in bpy.data.node_groups:
        if group.bl_idname == "ScriptingNodesTree":
            group.use_fake_user = True
            # add empty collection for node drawing
            if not "empty" in group.node_refs:
                group.node_refs.add().name = "empty"


def post_migration_cleanup(should_compile=True):
    """Run cleanup operations after migration to ensure all refs are synced.

    This is similar to what force_compile does - it ensures node refs
    are properly synced with their nodes after migration.

    Args:
        should_compile: Whether to compile the addon after cleanup
    """
    for ntree in bpy.data.node_groups:
        if ntree.bl_idname == "ScriptingNodesTree":
            for refs in ntree.node_refs:
                refs.clear_unused_refs()
                refs.fix_ref_names()
            # Reevaluate all nodes in the tree (same as force compile)
            ntree.reevaluate()
    if should_compile:
        compile_addon()


@persistent
def load_handler(dummy):
    clear_node_cache()
    if hasattr(bpy.context.scene, "sn"):
        bpy.context.scene.sn.picker_active = False
        subscribe_to_name_change()
        check_easy_bpy_install()
        # Migrate old data storage to new format (Blender 5.0 API changes)
        migrate_socket_data()
        migrate_node_ref_data()
        migrate_variable_data()
        migrate_scene_property_groups()
        # Sync refs with nodes after migration and optionally compile
        post_migration_cleanup(should_compile=bpy.context.scene.sn.compile_on_load)
        check_serpens_updates(bl_info["version"])
        bpy.ops.sn.reload_packages()
        load_snippets()
        bpy.context.scene.sn.hide_preferences = False
        unwatch_script_changes()
        if bpy.context.scene.sn.watch_script_changes:
            watch_script_changes()


@persistent
def unload_handler(dummy=None):
    if hasattr(bpy.context.scene, "sn"):
        unwatch_script_changes()
        unregister_addon()


@persistent
def undo_post(dummy=None):
    clear_node_cache()
    if hasattr(bpy.context, "space_data") and hasattr(
        bpy.context.space_data, "node_tree"
    ):
        ntree = bpy.context.space_data.node_tree
        if ntree.bl_idname == "ScriptingNodesTree":
            compile_addon()


@persistent
def save_pre(dummy=None):
    if bpy.context.scene.sn.watch_script_changes:
        update_script_nodes(True)
