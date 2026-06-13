import bpy
import time
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
from .node_tree.graphs.node_tree import ScriptingNodesTree
from .nodes.base_node import SN_ScriptingBaseNode


SOCKET_CONFIG_PROPERTIES = (
    "name",
    "subtype",
    "size",
    "size_editable",
    "dynamic",
    "prev_dynamic",
    "convert_data",
    "disabled",
    "can_be_disabled",
    "indexable",
    "index_type",
    "changeable",
    "data_type",
    "is_variable",
    "items",
    "custom_items_editable",
    "passthrough_layout_type",
)

_pending_migration_finalization = None


def _migration_values_equal(first, second):
    """Compare Blender values while tolerating IDProperty array conversions."""
    def comparable(value):
        if isinstance(value, (str, bytes, dict)):
            return value
        if isinstance(value, (list, tuple)):
            return tuple(comparable(item) for item in value)
        try:
            return tuple(comparable(item) for item in value)
        except TypeError:
            return value

    return comparable(first) == comparable(second)


def _coerce_legacy_property_value(socket, property_name, value):
    """Convert Blender's raw legacy RNA values to assignable Python values."""
    if not isinstance(value, int):
        return value

    if property_name == "subtype":
        subtypes = list(getattr(socket, "subtypes", ()))
        if 0 <= value < len(subtypes):
            return subtypes[value]

    if property_name == "data_type":
        try:
            items = socket.get_data_type_items(bpy.context)
            if 0 <= value < len(items):
                return items[value][0]
        except (AttributeError, IndexError, RuntimeError, TypeError):
            pass

    if property_name == "index_type":
        index_types = ("String", "Integer", "Property")
        if 0 <= value < len(index_types):
            return index_types[value]

    try:
        rna_property = socket.bl_rna.properties[property_name]
    except (AttributeError, KeyError):
        return value

    if rna_property.type != "ENUM":
        return value

    try:
        enum_items = list(rna_property.enum_items)
    except (AttributeError, TypeError):
        return value

    for item in enum_items:
        if item.value == value:
            return item.identifier

    if isinstance(value, int) and 0 <= value < len(enum_items):
        return enum_items[value].identifier

    return value


def _print_migration_warnings(warnings, heading="Migration Warning", limit=50):
    """Print a bounded warning list and preserve the useful summary."""
    for warning in warnings[:limit]:
        print(f"Serpens {heading}: {warning}")
    if len(warnings) > limit:
        print(
            f"Serpens: {len(warnings) - limit} additional"
            f" {heading.lower()}s omitted from console output"
        )


def _restore_pause_reregister(sn, value):
    """Restore the pause flag without invoking an implicit compilation."""
    previous_exporting = sn.is_exporting
    sn.is_exporting = True
    try:
        sn.pause_reregister = value
    finally:
        sn.is_exporting = previous_exporting


def _repair_compile_metadata(ntree):
    """Apply the reference fixes used by the manual force-compile operator."""
    for refs in ntree.node_refs:
        refs.clear_unused_refs()
        refs.fix_ref_names()
        if refs.name == "SN_OnKeypressNode":
            for node in refs.nodes:
                if node and getattr(node, "order", None) == 0:
                    node.order = 3


def _get_unavailable_custom_nodes():
    """Return placeholders for custom node classes unavailable in this install."""
    unavailable = []
    builtin_node_types = {"NodeFrame", "NodeReroute"}

    for ntree in bpy.data.node_groups:
        if ntree.bl_idname != "ScriptingNodesTree":
            continue
        for node in ntree.nodes:
            if getattr(node, "is_sn", False):
                continue
            if node.bl_idname in builtin_node_types:
                continue
            unavailable.append((ntree, node))

    return unavailable


def _print_unavailable_custom_nodes(unavailable, limit=25):
    """Explain missing package nodes without flooding the console."""
    if not unavailable:
        return

    print(
        "Serpens: Found"
        f" {len(unavailable)} unavailable custom/package nodes."
        " Migration will continue, but affected graph branches will remain"
        " inactive until their packages are restored."
    )
    for ntree, node in unavailable[:limit]:
        node_type = node.bl_idname or type(node).__name__
        print(
            "Serpens Missing Node:"
            f" tree={ntree.name!r}, node={node.name!r}, type={node_type!r}"
        )
    if len(unavailable) > limit:
        print(
            "Serpens:"
            f" {len(unavailable) - limit} additional missing nodes omitted"
        )


def _print_unavailable_custom_node_summary(count):
    """Repeat the missing package-node count at the end of loading."""
    if count:
        print(
            "Serpens: Load completed with"
            f" {count} unavailable custom/package nodes reported."
            " Install the missing packages to restore those graph branches."
        )


def _finalize_migrated_addon(
    filepath,
    previous_pause_reregister,
    should_compile,
    unavailable_custom_node_count,
):
    """Run a force-compile-equivalent pass after Blender's load timers settle."""
    global _pending_migration_finalization

    if _pending_migration_finalization != filepath:
        return None
    _pending_migration_finalization = None

    if bpy.data.filepath != filepath or not hasattr(bpy.context.scene, "sn"):
        return None

    started = time.perf_counter()
    sn = bpy.context.scene.sn
    print("Serpens: Finalizing migrated addon...")
    try:
        for ntree in bpy.data.node_groups:
            if ntree.bl_idname != "ScriptingNodesTree":
                continue
            _repair_compile_metadata(ntree)
            ntree.reevaluate()
    finally:
        _restore_pause_reregister(sn, previous_pause_reregister)

    if should_compile and not previous_pause_reregister:
        compile_addon()
    print(
        "Serpens: Migrated addon finalized in"
        f" {time.perf_counter() - started:.2f}s"
    )
    _print_unavailable_custom_node_summary(unavailable_custom_node_count)
    return None


def _schedule_migration_finalization(
    filepath,
    previous_pause_reregister,
    should_compile,
    unavailable_custom_node_count,
):
    """Defer final reevaluation until queued Blender node updates have run."""
    global _pending_migration_finalization

    _pending_migration_finalization = filepath
    bpy.app.timers.register(
        lambda: _finalize_migrated_addon(
            filepath,
            previous_pause_reregister,
            should_compile,
            unavailable_custom_node_count,
        ),
        first_interval=0.1,
    )


def _get_legacy_properties(item):
    """Get legacy properties with direct IDProperties taking precedence."""
    system_props = {}
    direct_props = {}

    try:
        props = item.bl_system_properties_get()
        if props:
            system_props = {key: props[key] for key in props.keys()}
    except (AttributeError, RuntimeError, TypeError, UnicodeDecodeError):
        pass

    try:
        if hasattr(item, "keys"):
            direct_props = {key: item[key] for key in list(item.keys())}
    except (RuntimeError, TypeError, KeyError, UnicodeDecodeError):
        pass

    # Older Serpens versions explicitly wrote widget values as socket
    # IDProperties, so those values are more authoritative than RNA defaults.
    properties = dict(system_props)
    properties.update(direct_props)
    return properties, system_props, direct_props


def _snapshot_socket_migration():
    """Capture legacy socket data before callbacks or relinking can mutate it."""
    snapshots = []

    for node_tree in bpy.data.node_groups:
        if node_tree.bl_idname != "ScriptingNodesTree":
            continue

        for node in node_tree.nodes:
            if not getattr(node, "is_sn", False):
                continue

            for is_output, sockets in ((False, node.inputs), (True, node.outputs)):
                for index, socket in enumerate(sockets):
                    if not getattr(socket, "is_sn", False):
                        continue

                    properties, system_props, direct_props = _get_legacy_properties(
                        socket
                    )
                    value_properties = set()
                    value_properties.update(
                        getattr(
                            socket,
                            "subtype_values",
                            {"NONE": "default_value"},
                        ).values()
                    )
                    value_properties.update(
                        {
                            "default_value",
                            "value_file_path",
                            "value_dir_path",
                            "color_value",
                            "color_alpha_value",
                            "factor_value",
                        }
                    )

                    snapshots.append(
                        {
                            "tree": node_tree,
                            "node": node,
                            "socket": socket,
                            "is_output": is_output,
                            "index": index,
                            "name": socket.name,
                            "properties": properties,
                            "system_properties": system_props,
                            "direct_properties": direct_props,
                            "value_properties": {
                                key: properties[key]
                                for key in value_properties
                                if key in properties
                            },
                            "config_properties": {
                                key: _coerce_legacy_property_value(
                                    socket, key, properties[key]
                                )
                                for key in SOCKET_CONFIG_PROPERTIES
                                if key in properties and hasattr(socket, key)
                            },
                        }
                    )

    return snapshots


def _socket_storage_key(snapshot, property_name):
    """Build the current parent-node storage key for a socket property."""
    socket = snapshot["socket"]
    key_prefix = socket._get_socket_storage_key()
    return f"{key_prefix}_{property_name}"


def _restore_socket_configuration(snapshots):
    """Restore socket UI configuration that survived in Blender's old storage."""
    restored_count = 0
    failed = []

    snapshots_by_node = {}
    for snapshot in snapshots:
        node_key = id(snapshot["node"])
        snapshots_by_node.setdefault(
            node_key,
            {"node": snapshot["node"], "snapshots": []},
        )["snapshots"].append(snapshot)

    for node_data in snapshots_by_node.values():
        node = node_data["node"]
        node_snapshots = node_data["snapshots"]
        previous_disable_evaluation = node.disable_evaluation
        node.disable_evaluation = True
        try:
            for snapshot in node_snapshots:
                socket = snapshot["socket"]
                for property_name, value in snapshot["config_properties"].items():
                    try:
                        current_value = getattr(socket, property_name)
                        if _migration_values_equal(current_value, value):
                            continue
                        if property_name == "name" and hasattr(
                            socket, "set_name_silent"
                        ):
                            socket.set_name_silent(value)
                        else:
                            setattr(socket, property_name, value)
                        restored_count += 1
                    except (
                        AttributeError,
                        RuntimeError,
                        TypeError,
                        ValueError,
                    ) as error:
                        failed.append(
                            f"{snapshot['node'].name}.{snapshot['name']}"
                            f" config {property_name}: {error}"
                        )
        finally:
            node.disable_evaluation = previous_disable_evaluation

    return restored_count, failed


def _write_socket_values(snapshots):
    """Write snapshotted widget values to parent-node storage."""
    migrated_count = 0
    overwritten_count = 0

    for snapshot in snapshots:
        node = snapshot["node"]
        for property_name, value in snapshot["value_properties"].items():
            storage_key = _socket_storage_key(snapshot, property_name)
            if storage_key in node:
                if _migration_values_equal(node[storage_key], value):
                    continue
                overwritten_count += 1
            node[storage_key] = value
            migrated_count += 1

    return migrated_count, overwritten_count


def _validate_socket_values(snapshots, phase):
    """Confirm migrated values remain readable under each socket's current key."""
    failures = []

    for snapshot in snapshots:
        node = snapshot["node"]
        for property_name, expected in snapshot["value_properties"].items():
            try:
                storage_key = _socket_storage_key(snapshot, property_name)
            except (AttributeError, ReferenceError, RuntimeError) as error:
                failures.append(
                    f"{phase}: {snapshot['node'].name}.{snapshot['name']}"
                    f" could not resolve its current storage key: {error}"
                )
                continue
            if storage_key not in node:
                failures.append(
                    f"{phase}: {snapshot['node'].name}.{snapshot['name']}"
                    f" missing {storage_key}"
                )
                continue
            actual = node[storage_key]
            if not _migration_values_equal(actual, expected):
                failures.append(
                    f"{phase}: {snapshot['node'].name}.{snapshot['name']}"
                    f" {property_name} expected {expected!r}, got {actual!r}"
                )

    return failures


def migrate_socket_data(snapshots=None):
    """Migrate old socket storage and return snapshots plus a result report.

    This handles files created before the Blender 5.0 API changes where
    bpy.props properties can no longer store IDProperties on NodeSocket.
    Old files stored widget values like socket["default_value"],
    but now we store them on the parent node with a unique key.

    There are two types of old storage:
    1. Custom IDProperties on socket (accessed via socket["key"] or socket.keys())
    2. Default bpy.props storage (accessed via socket.bl_system_properties_get())
    """
    if snapshots is None:
        snapshots = _snapshot_socket_migration()
    restored_count, config_failures = _restore_socket_configuration(snapshots)
    migrated_count, overwritten_count = _write_socket_values(snapshots)
    validation_failures = _validate_socket_values(snapshots, "before cleanup")

    direct_socket_count = sum(
        bool(item["direct_properties"]) for item in snapshots
    )
    system_socket_count = sum(
        bool(item["system_properties"]) for item in snapshots
    )
    source_conflicts = []
    for snapshot in snapshots:
        system_props = snapshot["system_properties"]
        direct_props = snapshot["direct_properties"]
        relevant_properties = set(snapshot["value_properties"])
        relevant_properties.update(snapshot["config_properties"])
        for property_name in relevant_properties & system_props.keys() & direct_props.keys():
            if not _migration_values_equal(
                system_props[property_name], direct_props[property_name]
            ):
                source_conflicts.append(
                    f"{snapshot['node'].name}.{snapshot['name']}"
                    f" {property_name}: system={system_props[property_name]!r},"
                    f" direct={direct_props[property_name]!r}; using direct"
                )
    print(
        "Serpens: Socket migration snapshot:"
        f" {len(snapshots)} sockets,"
        f" {direct_socket_count} with direct properties,"
        f" {system_socket_count} with system properties"
    )
    print(
        "Serpens: Socket migration wrote"
        f" {migrated_count} values"
        f" ({overwritten_count} replaced existing parent-node values)"
        f" and restored {restored_count} configuration values"
    )
    if source_conflicts:
        print(
            "Serpens: Found"
            f" {len(source_conflicts)} conflicting legacy socket values"
        )
        for conflict in source_conflicts[:25]:
            print(f"Serpens Migration Source Conflict: {conflict}")
        if len(source_conflicts) > 25:
            print(
                "Serpens: Additional source conflicts omitted from console output"
            )
    _print_migration_warnings(config_failures + validation_failures)

    return snapshots, {
        "config_failures": config_failures,
        "validation_failures": validation_failures,
    }


def _get_old_property_value(item, key):
    """Try to get an old property value from various storage methods.

    Returns the value if found, None otherwise.
    """
    properties, _, _ = _get_legacy_properties(item)
    return properties.get(key)


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


def migrate_portal_nodes():
    """Migrate portal nodes to ensure proper initialization after Blender 5.0 load.

    Portal nodes rely on:
    - _prev_var_name IDProperty for tracking name changes
    - use_custom_color enabled to show colors
    - color synced with custom_color
    - label synced with var_name
    - OUTPUT portals synced to their INPUT portal colors
    """
    migrated_count = 0

    # First pass: Initialize all portal nodes and collect INPUT portal colors
    input_colors = {}  # var_name -> custom_color tuple

    for ntree in bpy.data.node_groups:
        if ntree.bl_idname != "ScriptingNodesTree":
            continue

        for node in ntree.nodes:
            if node.bl_idname != "SN_PortalNode":
                continue

            actions = []

            # Initialize _prev_var_name if missing
            if node.get("_prev_var_name") is None:
                node["_prev_var_name"] = node.var_name
                actions.append("init _prev_var_name")

            # Enable use_custom_color
            try:
                if not node.use_custom_color:
                    node.use_custom_color = True
                    actions.append("enable use_custom_color")
            except Exception:
                pass

            # Sync display color with custom_color
            try:
                if tuple(node.color) != tuple(node.custom_color):
                    node.color = node.custom_color
                    actions.append("sync color")
            except Exception:
                pass

            # Restore label from var_name if empty
            if not node.label and node.var_name:
                node.label = node.var_name
                actions.append("restore label")

            # Collect INPUT portal colors
            if node.direction == "INPUT" and node.var_name:
                input_colors[node.var_name] = tuple(node.custom_color)

            if actions:
                migrated_count += 1

    # Second pass: Sync OUTPUT portal colors to their INPUT portals
    for ntree in bpy.data.node_groups:
        if ntree.bl_idname != "ScriptingNodesTree":
            continue

        for node in ntree.nodes:
            if node.bl_idname != "SN_PortalNode":
                continue

            if node.direction == "OUTPUT" and node.var_name in input_colors:
                target_color = input_colors[node.var_name]
                try:
                    if tuple(node.custom_color) != target_color:
                        node.custom_color = target_color
                        node.color = target_color
                        migrated_count += 1
                except Exception:
                    pass

    if migrated_count > 0:
        print(f"Serpens: Migrated {migrated_count} portal node properties")


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

    Existing links are replayed through the same link-insert callbacks used
    when a user connects sockets. This refreshes dynamic sockets and layout
    state without destructively removing and recreating every link.

    Args:
        should_compile: Whether to compile the addon after cleanup
    """
    node_trees = [
        ntree
        for ntree in bpy.data.node_groups
        if ntree.bl_idname == "ScriptingNodesTree"
    ]
    window_manager = bpy.context.window_manager
    total_trees = len(node_trees)
    total_work = sum(
        len(ntree.links)
        + sum(getattr(node, "is_sn", False) for node in ntree.nodes)
        for ntree in node_trees
    )
    completed_work = 0
    progress_interval = max(1, total_work // 100)

    if total_work:
        window_manager.progress_begin(0, total_work)

    try:
        for tree_index, ntree in enumerate(node_trees, start=1):
            tree_started = time.perf_counter()
            print(
                "Serpens: Refreshing migrated graph"
                f" {tree_index}/{total_trees}: {ntree.name}"
                f" ({len(ntree.nodes)} nodes, {len(ntree.links)} links)"
            )
            if total_work:
                window_manager.progress_update(completed_work)

            _repair_compile_metadata(ntree)

            SN_ScriptingBaseNode.batch_evaluation = True
            callback_started = time.perf_counter()
            # Replay the callbacks that normally run when each existing link
            # is inserted. Work from a snapshot because dynamic callbacks may
            # add sockets while the graph is refreshed.
            mapped_links = [
                ntree._map_link_to_sockets(link) for link in list(ntree.links)
            ]
            for from_socket, to_socket, from_real, _ in mapped_links:
                try:
                    if from_real:
                        if getattr(from_real.node, "is_sn", False):
                            from_real.node.link_insert(
                                from_real, to_socket, is_output=True
                            )
                        if getattr(to_socket.node, "is_sn", False):
                            to_socket.node.link_insert(
                                from_real, to_socket, is_output=False
                            )
                    elif (
                        from_socket
                        and getattr(from_socket.node, "is_sn", False)
                        and to_socket
                        and getattr(to_socket.node, "is_sn", False)
                    ):
                        from_socket.node.link_insert(
                            from_socket, to_socket, is_output=True
                        )
                except Exception:
                    pass
                completed_work += 1
                if completed_work % progress_interval == 0:
                    window_manager.progress_update(completed_work)
            callback_duration = time.perf_counter() - callback_started

            ScriptingNodesTree.link_cache[id(ntree)] = list(
                map(ntree._map_link_to_sockets, ntree.links.values())
            )

            evaluation_started = time.perf_counter()
            nodes = [
                node for node in ntree.nodes if getattr(node, "is_sn", False)
            ]
            dependencies = {node: set() for node in nodes}
            dependents = {node: set() for node in nodes}

            for link in ntree.links:
                from_socket, to_socket, from_real, _ = ntree._map_link_to_sockets(
                    link
                )
                source_socket = from_real or from_socket
                source_node = getattr(source_socket, "node", None)
                target_node = getattr(to_socket, "node", None)
                if source_node not in dependencies or target_node not in dependencies:
                    continue

                if getattr(source_socket, "is_program", False):
                    dependency, dependent = target_node, source_node
                else:
                    dependency, dependent = source_node, target_node

                if dependency != dependent:
                    dependencies[dependent].add(dependency)
                    dependents[dependency].add(dependent)

            ready = [node for node in nodes if not dependencies[node]]
            evaluation_order = []
            while ready:
                node = ready.pop()
                evaluation_order.append(node)
                for dependent in dependents[node]:
                    dependencies[dependent].discard(node)
                    if not dependencies[dependent]:
                        ready.append(dependent)

            # Cycles are legal in some data layouts. Preserve tree order for
            # anything that could not be topologically ordered.
            evaluated = set(evaluation_order)
            evaluation_order.extend(node for node in nodes if node not in evaluated)

            for node in evaluation_order:
                node._evaluate(bpy.context)
                completed_work += 1
                if completed_work % progress_interval == 0:
                    window_manager.progress_update(completed_work)
            evaluation_duration = time.perf_counter() - evaluation_started

            if total_work:
                window_manager.progress_update(completed_work)
            print(
                "Serpens: Refreshed graph"
                f" {tree_index}/{total_trees} in"
                f" {time.perf_counter() - tree_started:.2f}s"
                f" (links {callback_duration:.2f}s,"
                f" nodes {evaluation_duration:.2f}s)"
            )

        trigger_started = time.perf_counter()
        trigger_count = 0
        for ntree in node_trees:
            for node in ntree.nodes:
                if getattr(node, "is_sn", False) and getattr(
                    node, "is_trigger", False
                ):
                    node._evaluate(bpy.context)
                    trigger_count += 1
        print(
            "Serpens: Finalized"
            f" {trigger_count} trigger nodes in"
            f" {time.perf_counter() - trigger_started:.2f}s"
        )
    finally:
        SN_ScriptingBaseNode.batch_evaluation = False
        if total_work:
            window_manager.progress_end()

    if should_compile:
        compile_addon()


def _get_legacy_socket_evidence(snapshots):
    """Count legacy values that are not represented in parent-node storage."""
    candidates = []

    for snapshot in snapshots:
        node = snapshot["node"]
        direct_props = snapshot["direct_properties"]
        system_props = snapshot["system_properties"]

        for property_name, value in snapshot["value_properties"].items():
            if property_name in direct_props:
                source = "direct"
            elif property_name in system_props:
                source = "system"
            else:
                continue

            try:
                storage_key = _socket_storage_key(snapshot, property_name)
            except (AttributeError, ReferenceError, RuntimeError):
                continue

            if storage_key not in node or not _migration_values_equal(
                node[storage_key], value
            ):
                candidates.append(
                    {
                        "node": snapshot["node"].name,
                        "socket": snapshot["name"],
                        "property": property_name,
                        "source": source,
                        "storage_key": storage_key,
                    }
                )

    return candidates


def _get_blender_5_migration_status(sn):
    """Return migration eligibility and the reason for the decision."""
    serpens_tree_count = sum(
        ntree.bl_idname == "ScriptingNodesTree" for ntree in bpy.data.node_groups
    )

    # load_post also runs for Blender's startup file. A real opened .blend has
    # a filepath, while the default/startup session does not.
    if not bpy.data.filepath:
        return (
            False,
            "no loaded .blend filepath",
            serpens_tree_count,
            [],
            [],
        )

    if not serpens_tree_count:
        return (
            False,
            "no Serpens node trees found",
            serpens_tree_count,
            [],
            [],
        )

    snapshots = _snapshot_socket_migration()
    legacy_candidates = _get_legacy_socket_evidence(snapshots)
    if legacy_candidates:
        if sn.migrated_blender_5:
            reason = (
                "migration flag is set but"
                f" {len(legacy_candidates)} legacy socket values need recovery"
            )
        else:
            reason = (
                f"{len(legacy_candidates)} legacy socket values need recovery"
            )
        return True, reason, serpens_tree_count, snapshots, legacy_candidates

    if sn.migrated_blender_5:
        return (
            False,
            "migration flag is set and no legacy socket values need recovery",
            serpens_tree_count,
            snapshots,
            legacy_candidates,
        )

    return (
        True,
        "unmarked Serpens project detected",
        serpens_tree_count,
        snapshots,
        legacy_candidates,
    )


@persistent
def load_handler(dummy):
    load_started = time.perf_counter()
    clear_node_cache()
    if hasattr(bpy.context.scene, "sn"):
        sn = bpy.context.scene.sn
        previous_pause_reregister = sn.pause_reregister
        sn.picker_active = False
        subscribe_to_name_change()
        check_easy_bpy_install()

        (
            should_migrate,
            migration_reason,
            serpens_tree_count,
            socket_snapshots,
            legacy_candidates,
        ) = _get_blender_5_migration_status(sn)
        unavailable_custom_nodes = _get_unavailable_custom_nodes()
        if bpy.data.filepath:
            print(
                "Serpens: Migration check:"
                f" filepath={bpy.data.filepath!r},"
                f" scene={bpy.context.scene.name!r},"
                f" trees={serpens_tree_count},"
                f" migrated_flag={sn.migrated_blender_5!r},"
                f" recovery_candidates={len(legacy_candidates)},"
                f" decision={migration_reason}"
            )
            _print_unavailable_custom_nodes(unavailable_custom_nodes)

        # Only migrate a loaded Serpens project, never Blender's startup scene.
        migration_ready_for_finalization = False
        if should_migrate:
            migration_started = time.perf_counter()
            sn.pause_reregister = True
            print("Serpens: Running Blender 5.0 migration...")
            try:
                # Migrate old data storage to new format (Blender 5.0 API changes)
                socket_snapshots, socket_report = migrate_socket_data(
                    socket_snapshots
                )
                migrate_node_ref_data()
                migrate_variable_data()
                migrate_scene_property_groups()
                migrate_portal_nodes()
                # Sync refs with nodes and recalculate all links
                post_migration_cleanup(should_compile=False)
                post_cleanup_failures = _validate_socket_values(
                    socket_snapshots, "after cleanup"
                )
                _print_migration_warnings(post_cleanup_failures)

                migration_failures = (
                    socket_report["config_failures"]
                    + socket_report["validation_failures"]
                    + post_cleanup_failures
                )
                if migration_failures:
                    print(
                        "Serpens: Migration did not validate;"
                        " the file has not been marked as migrated"
                    )
                else:
                    sn.migrated_blender_5 = True
                    print("Serpens: Migration complete and validated")
                migration_ready_for_finalization = True
            finally:
                print(
                    "Serpens: Migration phase took"
                    f" {time.perf_counter() - migration_started:.2f}s"
                )
                if not migration_ready_for_finalization:
                    _restore_pause_reregister(sn, previous_pause_reregister)

        if migration_ready_for_finalization:
            _schedule_migration_finalization(
                bpy.data.filepath,
                previous_pause_reregister,
                sn.compile_on_load,
                len(unavailable_custom_nodes),
            )
        elif sn.compile_on_load:
            compile_started = time.perf_counter()
            compile_addon()
            print(
                "Serpens: Compile-on-load phase took"
                f" {time.perf_counter() - compile_started:.2f}s"
            )

        setup_started = time.perf_counter()
        check_serpens_updates(bl_info["version"])
        print(
            "Serpens: Update-check phase took"
            f" {time.perf_counter() - setup_started:.2f}s"
        )
        setup_started = time.perf_counter()
        bpy.ops.sn.reload_packages()
        load_snippets()
        print(
            "Serpens: Package/snippet phase took"
            f" {time.perf_counter() - setup_started:.2f}s"
        )
        sn.hide_preferences = False
        unwatch_script_changes()
        if sn.watch_script_changes:
            watch_script_changes()
        print(
            "Serpens: Load handler completed in"
            f" {time.perf_counter() - load_started:.2f}s"
        )
        if not migration_ready_for_finalization:
            _print_unavailable_custom_node_summary(
                len(unavailable_custom_nodes)
            )


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
