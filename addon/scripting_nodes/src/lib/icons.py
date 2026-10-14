"""Blender's built-in icons, and the button that picks one.

Built-in icons are stored by name ("MESH_DATA"): their numbers change between
Blender versions. Generated code turns names into numbers when it runs.

    draw_icon_picker(layout, socket, "value")
"""

import bpy

_names = None
_name_set = None


def builtin_icons() -> list[str]:
    """Names of all built-in icons, "NONE" first."""
    global _names, _name_set
    if _names is None:
        icon = bpy.types.UILayout.bl_rna.functions["prop"].parameters["icon"]
        _names = [item.identifier for item in icon.enum_items]
        _name_set = set(_names)
    return _names


def is_builtin(name: str) -> bool:
    builtin_icons()
    return name in _name_set


def draw_icon_picker(layout, owner, prop, show_name=False):
    """A button showing the icon named by `owner.<prop>` that opens a search
    of all built-in icons (sna.pick_icon)."""
    name = getattr(owner, prop)
    if not name:
        icon, text = "NONE", "None"
    else:
        # QUESTION: an icon of another Blender version
        icon = name if is_builtin(name) else "QUESTION"
        text = name if show_name else ""
    row = layout.row(align=True)
    row.context_pointer_set("sna_icon_owner", owner)
    row.operator("sna.pick_icon", text=text, icon=icon).prop_name = prop
    return row
