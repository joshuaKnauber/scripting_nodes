"""Helper functions of the add-on."""

import contextlib
import os

import bpy

_keymaps = []


def add_shortcut(
    keymap, space_type, idname, key, value="PRESS", properties=None, **modifiers
):
    """Add a keymap item to Blender's add-on keyconfig (removed when the
    add-on is disabled)."""
    keyconfig = bpy.context.window_manager.keyconfigs.addon
    if keyconfig is None:  # background mode
        return
    keymap = keyconfig.keymaps.new(name=keymap, space_type=space_type)
    item = keymap.keymap_items.new(idname, key, value, **modifiers)
    for name, prop_value in (properties or {}).items():
        setattr(item.properties, name, prop_value)
    _keymaps.append((keymap, item))


def redraw(area_type=""):
    """Redraw the editors of a type ("VIEW_3D"), all with ""."""
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if not area_type or area.type == area_type:
                area.tag_redraw()


def report(owner, kind, message):
    """Report a message from an operator (`owner`, shown in the status bar
    and the Info editor), printed where there is none."""
    message = str(message)
    if hasattr(owner, "report"):
        owner.report({kind}, message)
    else:
        print(f"{kind.title()}: {message}")


def write_text(path, text, append=False):
    """Write text to a file, creating its folder."""
    path = bpy.path.abspath(path)
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    with open(path, "a" if append else "w", encoding="utf-8") as file:
        file.write(str(text))


def unregister():
    for keymap, item in _keymaps:
        # gone if Blender removed the keymap already
        with contextlib.suppress(ReferenceError, RuntimeError):
            keymap.keymap_items.remove(item)
    _keymaps.clear()
