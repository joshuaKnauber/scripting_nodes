"""Shared helper functions of generated addons.

Nodes use them through `ctx.helper(name)`. Used helpers are written to
`_sn_helpers.py` in the generated addon. A helper can behave differently in
the live (dev) addon than in an exported one; this is the only place where
dev and export builds differ, nodes never check the build mode.
"""

import ast
from dataclasses import dataclass

from ..lib.code_format import sort_imports


@dataclass
class Helper:
    # source of the function in dev builds
    dev: str
    # source in exported builds, or None to use `export_name` instead
    export: str | None = None
    # name to call in exported builds instead of importing the helper
    export_name: str | None = None
    # statements run when the add-on is disabled (both builds)
    unregister: str | None = None
    # other helpers this one calls
    requires: tuple = ()


ICON_HELPER = '''
def sn_icon(icon):
    """Icon id of a built-in icon's name ("MESH_DATA"), 0 for unknown names.
    Icon ids pass through."""
    if not isinstance(icon, str):
        return icon or 0
    import bpy

    items = bpy.types.UILayout.bl_rna.functions["prop"].parameters["icon"].enum_items
    item = items.get(icon)
    return item.value if item else 0
'''

CUSTOM_ICON_HELPER = '''
_sn_previews = None


def sn_custom_icon(name):
    """Icon id of the image `icons/<name>` of this add-on (loaded once)."""
    global _sn_previews
    import os

    import bpy.utils.previews

    if _sn_previews is None:
        _sn_previews = bpy.utils.previews.new()
    if name not in _sn_previews:
        path = os.path.join(os.path.dirname(__file__), "icons", name)
        _sn_previews.load(name, path, "IMAGE")
    return _sn_previews[name].icon_id
'''

# UILayout.link is new in Blender 5.2, label_multiline / label_markdown after:
# older versions get a simpler version drawn with labels and buttons
TEXT_HELPERS = '''
def sn_label_multiline(layout, text, max_lines=0, alignment="LEFT", **icon):
    """layout.label_multiline(): text over several lines, wrapped."""
    if hasattr(layout, "label_multiline"):
        layout.label_multiline(
            text=text, max_lines=max_lines, alignment=alignment, **icon
        )
        return
    import textwrap

    import bpy

    region = bpy.context.region
    width = region.width if region else 300
    scale = bpy.context.preferences.system.ui_scale or 1.0
    chars = max(10, int(width / (7 * scale)))
    lines = []
    for paragraph in str(text).splitlines() or [""]:
        lines += textwrap.wrap(paragraph, chars) or [""]
    if max_lines:
        lines = lines[:max_lines]
    has_icon = any(value not in ("NONE", 0) for value in icon.values())
    column = layout.column(align=True)
    column.alignment = alignment
    for i, line in enumerate(lines):
        if i == 0 or not has_icon:
            column.label(text=line, **(icon if i == 0 else {}))
        else:
            column.label(text=line, icon="BLANK1")


def sn_label_markdown(layout, text):
    """layout.label_markdown(): headers, lists, quotes, links, rules."""
    if hasattr(layout, "label_markdown"):
        layout.label_markdown(text=text)
        return
    import re

    column = layout.column()
    for line in str(text).splitlines():
        line = line.strip()
        if re.fullmatch(r"(-{3,}|\\*{3,}|_{3,})", line):
            column.separator(type="LINE")
            continue
        line = re.sub(r"^[-+*]\\s+", "\\u2022 ", line)
        line = re.sub(r"^#{1,6}\\s+", "", line)
        line = re.sub(r"^>\\s?", "    ", line)
        line = re.sub(r"!?\\[([^\\]]*)\\]\\([^)]*\\)", r"\\1", line)
        line = re.sub(r"\\*\\*|\\*|`", "", line)
        if line:
            sn_label_multiline(column, line)
        else:
            column.separator()


def sn_textbox(layout, data, prop, lines=3, placeholder=""):
    """layout.textbox(): a multi-line text field (a normal one before)."""
    if hasattr(layout, "textbox"):
        layout.textbox(
            data, prop, initial_visible_lines=lines, placeholder=placeholder
        )
        return
    layout.prop(data, prop, text="", placeholder=placeholder)


def sn_link(layout, url, text="", **icon):
    """layout.link(): a button opening `url`."""
    if hasattr(layout, "link"):
        layout.link(url=url, text=text, **icon)
        return
    layout.operator("wm.url_open", text=text or url, **icon).url = url
'''


REPORT_HELPER = '''
def sn_report(owner, kind, message):
    """Report a message from an operator (`owner`, shown in the status bar
    and the Info editor), printed where there is none."""
    message = str(message)
    if hasattr(owner, "report"):
        owner.report({kind}, message)
    else:
        sn_print(f"{kind.title()}: {message}")
'''


TIMER_HELPERS = '''
_sn_timers = []


def sn_run_later(function, delay=0.0, persistent=False):
    """Call `function` once after `delay` seconds. Timers stop when the
    add-on is disabled (and when a file is loaded unless `persistent`)."""
    import bpy

    def timer():
        if timer in _sn_timers:
            _sn_timers.remove(timer)
        function()

    _sn_timers.append(timer)
    bpy.app.timers.register(
        timer, first_interval=max(0.0, delay), persistent=persistent
    )


def sn_run_in_intervals(function, interval, times=0, persistent=False):
    """Call `function(index)` every `interval` seconds: `times` times (0: no
    limit) or until it returns False."""
    import bpy

    index = 0

    def timer():
        nonlocal index
        keep_running = function(index)
        index += 1
        if keep_running is False or (times > 0 and index >= times):
            if timer in _sn_timers:
                _sn_timers.remove(timer)
            return None
        return max(0.01, interval)

    _sn_timers.append(timer)
    bpy.app.timers.register(timer, first_interval=0.0, persistent=persistent)
'''

TIMERS_UNREGISTER = """
import bpy

for timer in _sn_timers:
    if bpy.app.timers.is_registered(timer):
        bpy.app.timers.unregister(timer)
_sn_timers.clear()
"""


SHORTCUT_HELPER = '''
_sn_keymaps = []


def sn_add_shortcut(keymap, space_type, idname, key, value="PRESS", properties=None, **modifiers):
    """Add a keymap item to Blender's add-on keyconfig (removed when the
    add-on is disabled)."""
    import bpy

    keyconfig = bpy.context.window_manager.keyconfigs.addon
    if keyconfig is None:  # background mode
        return
    keymap = keyconfig.keymaps.new(name=keymap, space_type=space_type)
    item = keymap.keymap_items.new(idname, key, value, **modifiers)
    for name, prop_value in (properties or {}).items():
        setattr(item.properties, name, prop_value)
    _sn_keymaps.append((keymap, item))
'''


REDRAW_HELPER = '''
def sn_redraw(area_type=""):
    """Redraw the editors of a type ("VIEW_3D"), all with ""."""
    import bpy

    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            if not area_type or area.type == area_type:
                area.tag_redraw()
'''


# paths starting with // are relative to the .blend file (bpy.path.abspath)
FILE_HELPERS = '''
def sn_read_text(path):
    """The text of a file, "" if it doesn't exist."""
    import os

    import bpy

    path = bpy.path.abspath(path)
    if not os.path.isfile(path):
        return ""
    with open(path, encoding="utf-8") as file:
        return file.read()


def sn_write_text(path, text, append=False):
    """Write text to a file, creating its folder."""
    import os

    import bpy

    path = bpy.path.abspath(path)
    folder = os.path.dirname(path)
    if folder:
        os.makedirs(folder, exist_ok=True)
    with open(path, "a" if append else "w", encoding="utf-8") as file:
        file.write(str(text))


def sn_list_folder(folder, extension="", kind="FILES", full_paths=True):
    """Files and/or folders in a folder (sorted), [] if it doesn't exist.
    `extension` filters files (".png", case doesn't matter)."""
    import os

    import bpy

    folder = bpy.path.abspath(folder)
    if not os.path.isdir(folder):
        return []
    found = []
    for name in sorted(os.listdir(folder)):
        path = os.path.join(folder, name)
        if os.path.isdir(path):
            if kind == "FILES":
                continue
        elif kind == "FOLDERS" or not name.lower().endswith(extension.lower()):
            continue
        found.append(path if full_paths else name)
    return found


def sn_blend_contents(path, data_type):
    """Names of the data of a type ("materials") in a .blend file, sorted."""
    import os

    import bpy

    path = bpy.path.abspath(path)
    if not os.path.isfile(path):
        return []
    with bpy.data.libraries.load(path) as (data_from, _data_to):
        return sorted(getattr(data_from, data_type))


def sn_load_blend(path, data_type, names=None, link=False, add_to_scene=False):
    """Append (or link) data from a .blend file: the given names (a name or
    a list), all with none. Returns the loaded data."""
    import bpy

    if isinstance(names, str):
        names = [names] if names else None
    with bpy.data.libraries.load(bpy.path.abspath(path), link=link) as (
        data_from,
        data_to,
    ):
        available = getattr(data_from, data_type)
        wanted = available if names is None else [n for n in names if n in available]
        setattr(data_to, data_type, list(wanted))
    loaded = [data for data in getattr(data_to, data_type) if data is not None]
    if add_to_scene and data_type in ("objects", "collections"):
        collection = bpy.context.scene.collection
        for data in loaded:
            if data_type == "objects":
                collection.objects.link(data)
            else:
                collection.children.link(data)
    return loaded
'''


MSGBUS_HELPER = '''
from bpy.app.handlers import persistent

_sn_subscriptions = []
_sn_owner = object()


def _sn_subscribe_rna(key, notify):
    import bpy

    bpy.msgbus.subscribe_rna(
        key=key, owner=_sn_owner, args=(), notify=lambda *args: notify()
    )


@persistent
def _sn_resubscribe(*args):
    """Loading a file clears subscriptions."""
    for key, notify in _sn_subscriptions:
        _sn_subscribe_rna(key, notify)


def sn_subscribe(struct, prop, notify):
    """Call `notify()` when `prop` of any `struct` ("Object", "location")
    changes (bpy.msgbus), also after loading another file."""
    import bpy

    key = (getattr(bpy.types, struct), prop)
    _sn_subscriptions.append((key, notify))
    _sn_subscribe_rna(key, notify)
    if _sn_resubscribe not in bpy.app.handlers.load_post:
        bpy.app.handlers.load_post.append(_sn_resubscribe)
'''


TEXT_HELPER = '''
def sn_text(value):
    """A value as text: Blender data (objects, materials, ...) by its name."""
    import bpy

    if isinstance(value, bpy.types.bpy_struct):
        name = getattr(value, "name", None)
        if isinstance(name, str):
            return name
    return str(value)
'''


def _function(source, name):
    """The definition of `name` in `source` (up to the next one)."""
    start = source.index(f"def {name}(")
    end = source.find("\ndef ", start + 1)
    return source[start:] if end == -1 else source[start:end]


HELPERS = {
    "sn_print": Helper(
        dev='''
def sn_print(*args):
    """print() that also shows the message in the Scripting Nodes editor."""
    import bpy

    message = " ".join(str(arg) for arg in args)
    print(message)
    overlay = bpy.app.driver_namespace.get("_sn_overlay_log")
    if overlay:
        overlay("INFO", message)
''',
        export_name="print",
    ),
    "sn_icon": Helper(dev=ICON_HELPER, export=ICON_HELPER),
    "sn_text": Helper(dev=TEXT_HELPER, export=TEXT_HELPER),
    "sn_report": Helper(
        dev=REPORT_HELPER,
        # sn_print is print() in exported add-ons
        export=REPORT_HELPER.replace("sn_print(", "print("),
        requires=("sn_print",),
    ),
    **{
        name: Helper(
            dev=_function(TEXT_HELPERS, name),
            export=_function(TEXT_HELPERS, name),
            requires=("sn_label_multiline",) if name == "sn_label_markdown" else (),
        )
        for name in ("sn_label_multiline", "sn_label_markdown", "sn_link", "sn_textbox")
    },
    "sn_run_later": Helper(
        dev=TIMER_HELPERS[: TIMER_HELPERS.index("def sn_run_in_intervals(")],
        export=TIMER_HELPERS[: TIMER_HELPERS.index("def sn_run_in_intervals(")],
        unregister=TIMERS_UNREGISTER,
    ),
    "sn_run_in_intervals": Helper(
        dev=_function(TIMER_HELPERS, "sn_run_in_intervals"),
        export=_function(TIMER_HELPERS, "sn_run_in_intervals"),
        requires=("sn_run_later",),  # _sn_timers
    ),
    "sn_add_shortcut": Helper(
        dev=SHORTCUT_HELPER,
        export=SHORTCUT_HELPER,
        unregister="""
import contextlib

for keymap, item in _sn_keymaps:
    # gone if Blender removed the keymap already
    with contextlib.suppress(ReferenceError, RuntimeError):
        keymap.keymap_items.remove(item)
_sn_keymaps.clear()
""",
    ),
    "sn_subscribe": Helper(
        dev=MSGBUS_HELPER,
        export=MSGBUS_HELPER,
        unregister="""
import bpy

bpy.msgbus.clear_by_owner(_sn_owner)
if _sn_resubscribe in bpy.app.handlers.load_post:
    bpy.app.handlers.load_post.remove(_sn_resubscribe)
_sn_subscriptions.clear()
""",
    ),
    "sn_redraw": Helper(dev=REDRAW_HELPER, export=REDRAW_HELPER),
    **{
        name: Helper(
            dev=_function(FILE_HELPERS, name), export=_function(FILE_HELPERS, name)
        )
        for name in (
            "sn_read_text",
            "sn_write_text",
            "sn_list_folder",
            "sn_blend_contents",
            "sn_load_blend",
        )
    },
    "sn_custom_icon": Helper(
        dev=CUSTOM_ICON_HELPER,
        export=CUSTOM_ICON_HELPER,
        unregister="""
global _sn_previews
if _sn_previews is not None:
    import bpy.utils.previews

    bpy.utils.previews.remove(_sn_previews)
    _sn_previews = None
""",
    ),
}


def source(names, dev: bool) -> str:
    parts = []
    unregister = []
    for name in sorted(names):
        helper = HELPERS[name]
        code = helper.dev if dev else helper.export
        if code:
            parts.append(code.strip() + "\n")
        if helper.unregister:
            unregister.append(helper.unregister.strip())
    if unregister:
        body = "\n".join(unregister)
        parts.append(
            "def unregister():\n"
            + "".join(f"    {line}\n" if line else "\n" for line in body.splitlines())
        )
    code, imports = _hoist_imports("\n\n".join(parts))
    header = '"""Generated by Scripting Nodes."""\n'
    if imports:
        header += "\n" + "\n".join(sort_imports(imports)) + "\n"
    # isort: one blank line after the imports, two before a definition
    definition = code.startswith(("def ", "class ", "@"))
    return header + ("\n\n" if definition else "\n") + code


def needs_import(name: str, dev: bool) -> bool:
    helper = HELPERS[name]
    return dev or helper.export is not None


def call_name(name: str, dev: bool) -> str:
    helper = HELPERS[name]
    if not dev and helper.export is None and helper.export_name:
        return helper.export_name
    return name


def _hoist_imports(code: str) -> tuple[str, set[str]]:
    """Move the imports of `code` to the top of the module: the helpers are
    written as self-contained functions."""
    tree = ast.parse(code)
    lines = code.split("\n")
    imports, drop = set(), set()
    for node in ast.walk(tree):
        if (
            isinstance(node, (ast.Import, ast.ImportFrom))
            and node.lineno == node.end_lineno
        ):
            imports.add(lines[node.lineno - 1].strip())
            drop.add(node.lineno - 1)
            following = node.lineno
            if (
                following < len(lines)
                and not lines[following].strip()
                and node.col_offset
            ):
                drop.add(following)  # the blank line after an import in a function
    kept = [line for i, line in enumerate(lines) if i not in drop]
    return "\n".join(kept).strip("\n") + "\n", imports
