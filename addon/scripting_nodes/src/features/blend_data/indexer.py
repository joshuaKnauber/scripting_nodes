"""
Functions for indexing Blender RNA properties.
"""

import bpy
from typing import Any, List, Set, Tuple

from scripting_nodes.src.lib.utils.blend_data.path_utils import format_name
from scripting_nodes.src.features.blend_data.property_info import PropertyInfo
from scripting_nodes.src.features.blend_data.index import BlendDataIndex
from scripting_nodes.src.features.blend_data.constants import AREA_NAMES


def index_rna_properties(
    obj: Any,
    path: str,
    index: BlendDataIndex,
    visited_types: Set[str],
    depth: int = 0,
    max_depth: int = 4,
):
    """
    Recursively index properties from an RNA struct.

    Args:
        obj: The object to inspect
        path: Current access path (e.g., "bpy.data.objects[0]")
        index: The BlendDataIndex to populate
        visited_types: Set of already-visited RNA type names to avoid infinite recursion
        depth: Current recursion depth
        max_depth: Maximum recursion depth
    """
    if depth > max_depth:
        return

    if obj is None:
        return

    # Get the RNA type
    try:
        rna_type = type(obj).bl_rna
    except AttributeError:
        return

    rna_type_name = rna_type.identifier

    # Skip if we've already fully indexed this type
    if rna_type_name in visited_types:
        # Still add the access path for known properties
        for prop in rna_type.properties:
            if prop.identifier == "rna_type":
                continue
            key = f"{rna_type_name}.{prop.identifier}"
            if key in index.properties:
                index.properties[key].add_path(f"{path}.{prop.identifier}")
        return

    visited_types.add(rna_type_name)

    # Index all properties of this type
    for prop in rna_type.properties:
        prop_name = prop.identifier

        # Skip internal properties
        if prop_name in ("rna_type", "bl_rna"):
            continue

        prop_path = f"{path}.{prop_name}"

        prop_info = PropertyInfo(
            identifier=prop_name,
            name=prop.name or prop_name,  # Use display name, fall back to identifier
            description=prop.description or "",
            type_name=prop.type,
            rna_type=rna_type_name,
        )

        index.add_property(prop_info, prop_path)

        # Recurse into pointer and collection properties
        if prop.type == "POINTER" and hasattr(prop, "fixed_type"):
            try:
                child_obj = getattr(obj, prop_name, None)
                if child_obj is not None:
                    index_rna_properties(
                        child_obj, prop_path, index, visited_types, depth + 1, max_depth
                    )
            except Exception:
                pass

        elif prop.type == "COLLECTION":
            # Index the first item as a representative
            try:
                collection = getattr(obj, prop_name, None)
                if collection and len(collection) > 0:
                    first_item = collection[0]
                    item_path = f"{prop_path}[0]"
                    index_rna_properties(
                        first_item,
                        item_path,
                        index,
                        visited_types,
                        depth + 1,
                        max_depth,
                    )
            except Exception:
                pass


def get_area_contexts(window) -> List[Tuple[str, str, str]]:
    """
    Get list of available area contexts from the current window.
    Returns list of (identifier, name, description) for enum items.
    """
    items = [("CURRENT", "Current Context", "Use the current context")]

    if window is None:
        return items

    seen_types = set()
    for i, area in enumerate(window.screen.areas):
        area_type = area.type
        if area_type in seen_types:
            continue
        seen_types.add(area_type)

        name = AREA_NAMES.get(area_type, format_name(area_type))
        items.append((f"AREA_{i}", name, f"Index from {name} context"))

    return items


def _get_data_collections() -> List[str]:
    """Get all collection property names from bpy.data dynamically."""
    collections = []
    for prop in bpy.types.BlendData.bl_rna.properties:
        if prop.type == "COLLECTION":
            collections.append(prop.identifier)
    return collections


def _get_context_properties() -> List[str]:
    """Get all property names from bpy.context dynamically."""
    # Skip internal/private properties
    skip = {"bl_rna", "rna_type"}
    props = []
    for prop in bpy.types.Context.bl_rna.properties:
        if prop.identifier not in skip:
            props.append(prop.identifier)
    return props


def _index_bpy_data(index: BlendDataIndex, visited_types: Set[str], max_depth: int):
    """Index all bpy.data collections."""
    for collection_name in _get_data_collections():
        collection = getattr(bpy.data, collection_name, None)
        if collection is None:
            continue

        coll_path = f"bpy.data.{collection_name}"
        coll_info = PropertyInfo(
            identifier=collection_name,
            name=format_name(collection_name),
            description=f"Collection of {collection_name}",
            type_name="COLLECTION",
            rna_type="BlendData",
        )
        index.add_property(coll_info, coll_path)

        # Index first item if available
        try:
            if len(collection) > 0:
                first_item = collection[0]
                item_path = f"{coll_path}[0]"
                index_rna_properties(
                    first_item,
                    item_path,
                    index,
                    visited_types,
                    depth=1,
                    max_depth=max_depth,
                )
        except Exception:
            pass


def _index_bpy_context(
    index: BlendDataIndex, visited_types: Set[str], max_depth: int, ctx
):
    """Index all bpy.context properties."""
    for attr_name in _get_context_properties():
        try:
            attr_value = getattr(ctx, attr_name, None)
            if attr_value is None:
                continue

            attr_path = f"bpy.context.{attr_name}"

            # Add the context attribute itself as a property
            try:
                rna_type_name = (
                    type(attr_value).bl_rna.identifier
                    if hasattr(type(attr_value), "bl_rna")
                    else "Unknown"
                )
            except:
                rna_type_name = "Unknown"

            ctx_prop_info = PropertyInfo(
                identifier=attr_name,
                name=format_name(attr_name),
                description=f"Context {attr_name}",
                type_name="POINTER",
                rna_type="Context",
            )
            index.add_property(ctx_prop_info, attr_path)

            # Handle collections (like selected_objects)
            if hasattr(attr_value, "__iter__") and not isinstance(attr_value, str):
                try:
                    items = list(attr_value)
                    if items:
                        index_rna_properties(
                            items[0],
                            f"{attr_path}[0]",
                            index,
                            visited_types,
                            depth=1,
                            max_depth=max_depth,
                        )
                except Exception:
                    pass
            else:
                index_rna_properties(
                    attr_value,
                    attr_path,
                    index,
                    visited_types,
                    depth=1,
                    max_depth=max_depth,
                )
        except Exception:
            pass


def build_blend_data_index(
    max_depth: int = 4,
    context_override: dict = None,
    context_description: str = "Current Context",
) -> BlendDataIndex:
    """
    Build a complete index of all blend data properties.

    Args:
        max_depth: How deep to recurse into nested properties
        context_override: Optional context override dict for temp_override
        context_description: Description of the context being indexed

    Returns:
        The populated BlendDataIndex
    """
    index = BlendDataIndex()
    index.clear()
    index.indexed_context = context_description

    visited_types: Set[str] = set()

    # Index bpy.data collections
    _index_bpy_data(index, visited_types, max_depth)

    # Index bpy.context
    if context_override:
        with bpy.context.temp_override(**context_override):
            _index_bpy_context(index, visited_types, max_depth, bpy.context)
    else:
        _index_bpy_context(index, visited_types, max_depth, bpy.context)

    index.is_indexed = True
    return index
