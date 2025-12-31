"""
Utilities for working with Blender data paths.

This module provides common functions for:
- Formatting property names for display
- Parsing blend data paths into segments
- Creating node labels from paths
- Inferring socket types from property names
"""

import re
from typing import List, Optional


def format_name(text: str) -> str:
    """
    Format a snake_case or identifier into a readable title.

    Examples:
        "use_auto_smooth" → "Use Auto Smooth"
        "colorspace_settings" → "Colorspace Settings"
    """
    return text.replace("_", " ").title()


def singularize(name: str) -> str:
    """
    Simple singularization for common English plural patterns.

    Examples:
        "Libraries" → "Library"
        "Meshes" → "Mesh"
        "Images" → "Image"
        "Scenes" → "Scene"
    """
    if name.endswith("ies"):
        return name[:-3] + "y"  # Libraries → Library
    elif (
        name.endswith("shes")
        or name.endswith("ches")
        or name.endswith("xes")
        or name.endswith("zes")
    ):
        return name[:-2]  # Meshes → Mesh, Brushes → Brush
    elif name.endswith("s") and not name.endswith("ss"):
        return name[:-1]  # Images → Image, Scenes → Scene
    return name


def get_label_from_path(
    path: str, access_mode: str = "NONE", default_label: str = "Blend Data"
) -> str:
    """
    Get a concise node label from a blend data path.

    Args:
        path: The blend data path (e.g., "bpy.context.scene.render.fps")
        access_mode: The access mode ("NONE", "INDEX", or "NAME")
        default_label: Label to return if path is empty

    Examples:
        "bpy.context.scene" → "Scene"
        "bpy.data.images" → "Images"
        "bpy.context.scene.render.fps" → "Scene › Render › FPS"
        "colorspace_settings.name" → "Colorspace Settings › Name"
    """
    if not path:
        return default_label

    parts = path.split(".")

    # Remove bpy prefix parts
    if parts[0] == "bpy":
        parts = parts[1:]
    if parts and parts[0] in ("context", "data"):
        parts = parts[1:]

    if not parts:
        return default_label

    # Format each part
    formatted = [format_name(p) for p in parts]

    # For short paths, show the last element as main label
    if len(formatted) == 1:
        return formatted[0]

    # For longer paths, use arrow notation for clarity
    return " › ".join(formatted)


def get_socket_name_from_path(path: str, access_mode: str = "NONE") -> str:
    """
    Get an output socket name from a path.

    Args:
        path: The blend data path
        access_mode: The access mode - if INDEX or NAME, singularizes the result

    Examples:
        "bpy.data.images" with INDEX → "Image"
        "bpy.context.scene" → "Scene"
        "colorspace_settings.name" → "Name"
    """
    if not path:
        return "Data"

    # Get the last part of the path
    last_part = path.split(".")[-1]
    name = format_name(last_part)

    # If accessing by index/name, use singular form for collection items
    if access_mode in ("INDEX", "NAME"):
        name = singularize(name)

    return name


def get_input_name_from_path(path: str, access_mode: str = "NONE") -> str:
    """
    Get an input socket name based on the path that will connect to it.

    Args:
        path: The path of the node that will connect to this input
        access_mode: The access mode of the connecting node

    Examples:
        "bpy.data.images" with INDEX → "Image"
        "bpy.context.scene" → "Scene"
    """
    if not path:
        return "Data"

    last_part = path.split(".")[-1]
    name = format_name(last_part)

    if access_mode in ("INDEX", "NAME"):
        name = singularize(name)

    return name


def infer_output_type(prop_name: str) -> str:
    """
    Infer the output socket type based on property name.

    Args:
        prop_name: The property name (e.g., "name", "index", "enabled")

    Returns:
        Socket type identifier string
    """
    prop_lower = prop_name.lower()

    # String properties
    if prop_lower in (
        "name",
        "type",
        "mode",
        "filepath",
        "filename",
        "directory",
        "text",
        "label",
        "description",
        "path",
        "title",
    ):
        return "ScriptingStringSocket"

    # Integer properties
    if prop_lower in (
        "index",
        "count",
        "frame",
        "frame_current",
        "frame_start",
        "frame_end",
        "resolution_x",
        "resolution_y",
        "samples",
    ):
        return "ScriptingIntegerSocket"

    # Boolean properties
    if prop_lower in (
        "enabled",
        "active",
        "visible",
        "selected",
        "hide",
        "mute",
        "lock",
        "locked",
    ):
        return "ScriptingBooleanSocket"
    if (
        prop_lower.startswith("use_")
        or prop_lower.startswith("is_")
        or prop_lower.startswith("show_")
    ):
        return "ScriptingBooleanSocket"

    # Float properties
    if prop_lower in (
        "alpha",
        "strength",
        "factor",
        "value",
        "distance",
        "size",
        "width",
        "height",
        "fps",
        "speed",
        "scale",
    ):
        return "ScriptingFloatSocket"

    # Default to BlendData for complex/unknown types
    return "ScriptingBlendDataSocket"


def parse_blend_data_path(path: str) -> List[dict]:
    """
    Parse a blend data path into segments for node creation.
    Only splits at indexed access points like [0] or ["name"].

    Args:
        path: The full blend data path (e.g., "bpy.data.images[0].colorspace_settings.name")

    Returns:
        List of segment dictionaries with keys:
        - path: The path segment
        - is_root: Whether this is the first segment
        - access: Access mode ("NONE", "INDEX", or "NAME")
        - access_value: The index or name value (if applicable)
        - output_type: Socket type for the output
        - input_name: Name for the input socket (for non-root segments)

    Examples:
        "bpy.context.scene.render.fps" → 1 segment with full path
        "bpy.data.images[0].colorspace_settings.name" → 2 segments:
            - bpy.data.images with INDEX access
            - colorspace_settings.name as continuation
    """
    segments = []
    path = path.strip()

    if not path.startswith("bpy."):
        return segments

    # Split the path at indexed access points
    split_segments = _split_at_indexed_access(path)

    for i, seg_info in enumerate(split_segments):
        is_first = i == 0
        is_last = i == len(split_segments) - 1

        seg_path = seg_info["path"]
        access_mode = seg_info.get("access", "NONE")
        access_value = seg_info.get("access_value", None)

        # Infer output type from the last property in this segment
        last_prop = seg_path.split(".")[-1] if "." in seg_path else seg_path
        if is_last and access_mode == "NONE":
            output_type = infer_output_type(last_prop)
        else:
            output_type = "ScriptingBlendDataSocket"

        segment = {
            "path": seg_path,
            "is_root": is_first,
            "access": access_mode,
            "output_type": output_type,
        }

        if access_value is not None:
            segment["access_value"] = access_value

        segments.append(segment)

    # Calculate input names for non-root segments based on previous segment's output
    for i in range(1, len(segments)):
        prev_seg = segments[i - 1]
        prev_path = prev_seg["path"]
        prev_access = prev_seg.get("access", "NONE")
        segments[i]["input_name"] = get_input_name_from_path(prev_path, prev_access)

    return segments


def _split_at_indexed_access(path: str) -> List[dict]:
    """
    Split a path only at indexed access points.

    Internal function used by parse_blend_data_path.
    """
    segments = []
    pattern = re.compile(r"\[([^\]]+)\]")

    current_start = 0
    pos = 0

    while pos < len(path):
        match = pattern.search(path, pos)

        if not match:
            remainder = path[current_start:]
            if remainder:
                if remainder.startswith("."):
                    remainder = remainder[1:]
                if remainder:
                    segments.append({"path": remainder, "access": "NONE"})
            break

        bracket_start = match.start()
        bracket_end = match.end()
        accessor = match.group(1)

        segment_path = path[current_start:bracket_start]
        if segment_path.startswith("."):
            segment_path = segment_path[1:]

        if accessor.isdigit():
            access_mode = "INDEX"
            access_value = int(accessor)
        elif accessor.startswith('"') or accessor.startswith("'"):
            access_mode = "NAME"
            access_value = accessor.strip("\"'")
        else:
            access_mode = "NAME"
            access_value = accessor

        if segment_path:
            segments.append(
                {
                    "path": segment_path,
                    "access": access_mode,
                    "access_value": access_value,
                }
            )

        current_start = bracket_end
        pos = bracket_end

    # Handle case where path has no indexed access at all
    if not segments and path:
        segments.append({"path": path, "access": "NONE"})

    return segments


def extract_property_name(path: str) -> str:
    """
    Extract the last property name from a path.

    Args:
        path: A blend data path

    Returns:
        The last segment of the path (the property name)

    Examples:
        "bpy.context.scene.render.fps" → "fps"
        "colorspace_settings.name" → "name"
    """
    if not path:
        return ""
    return path.split(".")[-1]


def get_data_path_without_property(path: str) -> str:
    """
    Get the data path without the final property.

    Args:
        path: A blend data path

    Returns:
        The path without the last segment

    Examples:
        "bpy.context.scene.render.fps" → "bpy.context.scene.render"
        "bpy.context.scene" → "bpy.context"
    """
    if not path:
        return ""
    parts = path.split(".")
    if len(parts) <= 1:
        return ""
    return ".".join(parts[:-1])
