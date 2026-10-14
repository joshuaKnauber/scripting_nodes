"""Icons in generated code: the argument for layout calls, and image files
shipped as custom icons.

    args.append(icon_argument(ctx))  # "icon='MESH_DATA'", "icon_value=..."
"""

import os
import re

import bpy

from ..core.context import NodeError
from ..lib.icons import is_builtin


def icon_argument(ctx, key="icon"):
    """`icon='NAME'` for a picked built-in icon, `icon_value=...` for a
    connected one, None without an icon."""
    socket = ctx.node.socket(key)
    if socket.is_linked:
        return f"icon_value={ctx.input(key)}"
    return builtin_icon(socket.value)


def builtin_icon(name):
    """`icon='NAME'`, None for "". Raises NodeError for names Blender
    doesn't know (icons of another version)."""
    if not name:
        return None
    if not is_builtin(name):
        raise NodeError(f"Blender has no icon '{name}'")
    return f"icon={name!r}"


def icon_value(ctx, key="icon"):
    """The icon of input `key` as a value: an icon id, or the name of a
    picked built-in icon (enum items take both)."""
    socket = ctx.node.socket(key)
    if socket.is_linked:
        return ctx.input(key)
    builtin_icon(socket.value)
    return repr(socket.value or "NONE")


# -----------------------------------------------------------------------------
# Image files
# -----------------------------------------------------------------------------

_FORMAT_EXTENSIONS = {"JPEG": ".jpg", "TARGA": ".tga", "TARGA_RAW": ".tga"}
# (image pointer, path or packed size, mtime) -> bytes of the last read
_cache: dict = {}


def image_file(image: bpy.types.Image) -> tuple[str, bytes]:
    """(file name, contents) of an image to ship as an icon: its packed data
    or the file it was loaded from. Raises NodeError if it has neither."""
    if image.source != "FILE":
        raise NodeError(f"'{image.name}' isn't from a file: save or pack it first")
    path = bpy.path.abspath(image.filepath, library=image.library)
    extension = os.path.splitext(image.filepath)[1].lower()
    if not extension:
        format = image.file_format
        extension = _FORMAT_EXTENSIONS.get(format, "." + format.lower())
    stem = os.path.splitext(image.name)[0]
    name = (re.sub(r"[^\w-]", "_", stem) or "icon") + extension
    if image.packed_file is not None:
        key = (image.as_pointer(), image.packed_file.size, None)
        return name, _cached(key, lambda: bytes(image.packed_file.data))
    try:
        mtime = os.path.getmtime(path)
    except OSError:
        raise NodeError(
            f"Can't find the file of '{image.name}' ({path}): "
            "pack the image or fix its path"
        ) from None

    def read():
        with open(path, "rb") as f:
            return f.read()

    return name, _cached((image.as_pointer(), path, mtime), read)


def _cached(key, load):
    if key not in _cache:
        if len(_cache) > 64:
            _cache.clear()
        _cache[key] = load()
    return _cache[key]
