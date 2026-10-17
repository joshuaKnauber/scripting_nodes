"""The path browser's state: where it is and the entries of its columns
(`window_manager.sna_browser`, not saved). blend_data/ops/browser.py opens
it from a node, blend_data/ui/browser.py draws it.

The browser is at a Location (locations.py), stored as a Python path. Its
columns are the steps of that path, like a file browser's: the start
(Context / Blend File), then what each step contains, the entry the path
continues with active. Only the last COLUMNS columns are shown, so there
are that many slots. A path ending at a plain value shows the value in the
last column.

Clicking an entry (a list's active index changing) moves the browser and
fills the slots again. Entries are only rebuilt when the browser moves, so
the values they show are from then.
"""

import math
import textwrap

import bpy

from . import locations, rna

COLUMNS = 4
# arrays up to this length show their values, longer ones their size
MAX_ARRAY = 4

_filling = False


def location(context) -> locations.Location:
    return locations.free_location(context.window_manager.sna_browser.path)


def go(context, target: locations.Location):
    state = context.window_manager.sna_browser
    state.path = target.python() if target.root else ""
    fill(context)


def _open_entry(self, context):
    if _filling or not 0 <= self.active < len(self.entries):
        return
    go(context, locations.free_location(self.entries[self.active].target))


def _open_result(self, context):
    if _filling or not 0 <= self.result_active < len(self.results):
        return
    target = self.results[self.result_active].target
    self.search = ""  # fills
    go(context, locations.free_location(target))


def _search(self, context):
    if not _filling:
        fill_results(context)


def _show_all(self, context):
    if not _filling:
        fill(context)


class SNA_BrowserEntry(bpy.types.PropertyGroup):
    # name: the text shown
    summary: bpy.props.StringProperty()
    icon: bpy.props.StringProperty(default="BLANK1")
    opens: bpy.props.BoolProperty()
    target: bpy.props.StringProperty()  # where it leads (Python path)


class SNA_BrowserColumn(bpy.types.PropertyGroup):
    title: bpy.props.StringProperty()
    at: bpy.props.StringProperty()  # where in the path the column is
    filter: bpy.props.StringProperty(
        name="Filter",
        description="Only show entries containing these words",
        options={"TEXTEDIT_UPDATE", "SKIP_SAVE"},
    )
    entries: bpy.props.CollectionProperty(type=SNA_BrowserEntry)
    active: bpy.props.IntProperty(default=-1, update=_open_entry)
    note: bpy.props.StringProperty()  # why there are no live values
    # a plain value instead of entries
    is_value: bpy.props.BoolProperty()
    value: bpy.props.StringProperty()
    description: bpy.props.StringProperty()


class SNA_BrowserState(bpy.types.PropertyGroup):
    path: bpy.props.StringProperty()
    node_id: bpy.props.StringProperty()  # the node it picks a path for
    columns: bpy.props.CollectionProperty(type=SNA_BrowserColumn)
    shown: bpy.props.IntProperty()  # slots in use
    search: bpy.props.StringProperty(
        name="Search",
        description="Search all paths from where the browser starts",
        options={"TEXTEDIT_UPDATE", "SKIP_SAVE"},
        update=_search,
    )
    results: bpy.props.CollectionProperty(type=SNA_BrowserEntry)
    result_active: bpy.props.IntProperty(default=-1, update=_open_result)
    show_all: bpy.props.BoolProperty(
        name="Empty and Internal",
        description="Also show empty data and read-only values",
        update=_show_all,
    )


def prepare(context):
    """Create the slots (not from update callbacks: adding to a collection
    can move its items)."""
    state = context.window_manager.sna_browser
    while len(state.columns) < COLUMNS:
        state.columns.add()


# -----------------------------------------------------------------------------
# Filling the columns
# -----------------------------------------------------------------------------


def fill(context):
    global _filling
    state = context.window_manager.sna_browser
    here = location(context)
    steps = [None] + (list(range(len(here.parts) + 1)) if here.root else [])
    steps = steps[-COLUMNS:]
    # filters stay with their place when the columns move along
    filters = {slot.at: slot.filter for slot in state.columns if slot.filter}
    _filling = True
    try:
        for slot, count in zip(state.columns, steps):
            _fill_column(slot, context, here, count, filters)
        state.shown = len(steps)
    finally:
        _filling = False


def _fill_column(slot, context, here, count, filters):
    slot.entries.clear()
    slot.note = ""
    slot.is_value = False
    slot.active = -1
    at = here.truncated(count) if count is not None else None
    slot.at = at.python() if at is not None else "start"
    slot.filter = filters.get(slot.at, "")
    if at is None:
        _fill_start(slot, context, here)
        return
    slot.title = at.crumbs()[-1][0]
    try:
        value = locations.evaluate(at, context)
    except locations.Unavailable as error:
        if at.root != "INPUT":
            slot.note = f"{error}: what could be there"
        _static_entries(slot, at)
    else:
        if locations.is_collection(value):
            _item_entries(slot, at, value)
        elif locations.is_struct(value):
            _member_entries(slot, context, at, value)
        else:
            _value(slot, at, value)
    nxt = here.truncated(count + 1).python() if count < len(here.parts) else None
    for index, entry in enumerate(slot.entries):
        if entry.target == nxt:
            slot.active = index
            break


def _fill_start(slot, context, here):
    """Context, Blend File and the node's Data input."""
    slot.title = "Start"
    _add(slot.entries, "Context", "Active, selected, ...", "WINDOW", True,
         "bpy.context")  # fmt: skip
    _add(slot.entries, "Blend File", "All of the file's data", "FILE_BLEND", True,
         "bpy.data")  # fmt: skip
    node = browsed_node(context)
    data_input = locations.input_location(node) if node is not None else None
    if data_input is not None:
        if data_input.root == "INPUT":
            summary = (
                rna.display_name(data_input.input_type)
                if data_input.input_type
                else "Any"
            )
        else:
            summary = data_input.crumbs()[-1][0]
        _add(slot.entries, "Data Input", summary, "LINKED", True, data_input.python())
    if not here.root:
        return
    if data_input is not None and (
        here.root == "INPUT"
        or (data_input.root != "INPUT" and locations.continues(here, data_input))
    ):
        slot.active = 2
    else:
        slot.active = 0 if here.root == "CONTEXT" else 1


def browsed_node(context):
    from ..lib.trees import node_by_id

    node_id = context.window_manager.sna_browser.node_id
    return node_by_id(node_id) if node_id else None


def problem(context) -> str:
    """Why Use Path can't use where the browser is ("" if it can)."""
    here = location(context)
    node = browsed_node(context)
    if not here.root:
        return "Pick where the path starts"
    if node is not None and not node.path_accepts(here.final_step()):
        return "This node needs a property: pick a value"
    return ""


def _add(entries, text, summary, icon, opens, target):
    entry = entries.add()
    entry.name = text
    entry.summary = summary
    entry.icon = icon or "BLANK1"
    entry.opens = opens
    entry.target = target


def _member_entries(slot, context, at, value):
    show_all = context.window_manager.sna_browser.show_all
    data, values = [], []
    for identifier, text, prop in locations.struct_members(value, context):
        kind = prop.type if prop is not None else _kind(value, identifier)
        try:
            current = getattr(value, identifier)
        except AttributeError:
            current = None
        target = at.extended(identifier).python()
        if kind in {"POINTER", "COLLECTION"}:
            empty = current is None or (
                locations.is_collection(current) and not len(current)
            )
            if empty and not show_all:
                continue
            summary = _summary(current)
            if summary.replace(" ", "").lower() == text.replace(" ", "").lower():
                summary = ""  # "Field Settings: Field Settings"
            data.append((text, summary, _icon(current), True, target))
        else:
            if (prop is None or prop.is_readonly) and not show_all:
                continue
            values.append((text, _value_text(prop, current), None, False, target))
    if isinstance(value, bpy.types.Context):  # the common ones first
        data.sort(key=lambda d: d[4].rsplit(".", 1)[-1] not in rna.COMMON_CONTEXT)
    for entry in data + values:
        _add(slot.entries, *entry)


def _item_entries(slot, at, value):
    if (
        getattr(value, "active", None) is not None
        and rna.member(at.final_step(), "active").known
    ):
        _add(slot.entries, "Active", _summary(value.active), "LAYER_ACTIVE", True,
             at.extended("active").python())  # fmt: skip
    for index, item in enumerate(value):
        key = locations.item_key(value, index, item)
        _add(
            slot.entries,
            key.label(),
            "",
            _icon(item),
            True,
            at.extended(key=key).python(),
        )


def _static_entries(slot, at):
    step = at.final_step()
    if not step.known or not step.rna_type:
        return
    if step.collection:  # one item stands for all
        if rna.member(step, "active").known:
            _add(slot.entries, "Active", rna.display_name(step.rna_type),
                 "LAYER_ACTIVE", True, at.extended("active").python())  # fmt: skip
        key = locations.Key("INDEX", 0)
        _add(slot.entries, key.label(), rna.display_name(step.rna_type), None, True,
             at.extended(key=key).python())  # fmt: skip
        return
    for member in rna.members(step):
        opens = bool(member.rna_type)
        _add(slot.entries, rna.label(member), rna.type_label(member), None, opens,
             at.extended(member.name).python())  # fmt: skip


def _value(slot, at, value):
    step = at.final_step()
    prop = step.prop
    slot.is_value = True
    slot.value = _value_text(prop, value) if prop is not None else str(value)
    slot.description = prop.description if prop is not None else ""
    slot.title = f"{slot.title} ({rna.type_label(step) or type(value).__name__})"


def fill_results(context):
    """The search results: the live data below where the browser is first
    (finds what only exists on subtypes, like a Bevel modifier's width),
    then all paths of the types from its start."""
    global _filling
    state = context.window_manager.sna_browser
    here = location(context)
    start = locations.Location(here.root or "CONTEXT", input_type=here.input_type)
    words = state.search.lower().replace("_", " ").split()
    _filling = True
    try:
        state.results.clear()
        state.result_active = -1
        if not words:
            return
        seen = set()
        if here.root:
            for text, summary, opens, target in _live_search(context, here, words):
                seen.add(target)
                _add(state.results, text, summary, None, opens, target)
        node = browsed_node(context)
        accept = node.path_accepts if node is not None else None
        for found in rna.search(
            start.root_step(), state.search, accept=accept, limit=100
        ):
            parts = rna.segments(found.path)
            keys = [locations.Key("INDEX", 0)] * parts.count(rna.SUBSCRIPT)
            target = locations.Location(
                start.root, parts, keys, start.input_type
            ).python()
            if target not in seen:
                _add(state.results, found.text, found.type_label, None,
                     bool(found.final.rna_type), target)  # fmt: skip
    finally:
        _filling = False


def _live_search(context, start, words, depth=4, budget=6000, limit=60):
    """(text, summary, opens, target) of the data below `start` whose labels
    contain all `words` (the last one in its own label), nearest first."""
    try:
        value = locations.evaluate(start, context)
    except locations.Unavailable:
        return []
    found = []
    visited = set()
    frontier = [(start, value, ())]
    for _ in range(depth):
        following = []
        for at, current, labels in frontier:
            for target, child, text in _children(context, at, current):
                budget -= 1
                if budget < 0:
                    return found
                path_labels = labels + (text,)
                haystack = " ".join(path_labels).lower()
                opens = locations.is_struct(child) or locations.is_collection(child)
                if words[-1] in text.lower() and all(w in haystack for w in words):
                    summary = _summary(child) if opens else _plain(target, child)
                    found.append((" › ".join(path_labels), summary, opens,
                                  target.python()))  # fmt: skip
                    if len(found) >= limit:
                        return found
                if opens:
                    pointer = (
                        child.as_pointer() if locations.is_struct(child) else id(child)
                    )
                    if pointer not in visited:
                        visited.add(pointer)
                        following.append((target, child, path_labels))
        frontier = following
    return found


def _children(context, at, value):
    """(location, value, label) of what's in `value`: members of a struct,
    the first items of a collection."""
    if locations.is_collection(value):
        for index, item in enumerate(value):
            if index >= 20:
                break
            key = locations.item_key(value, index, item)
            yield at.extended(key=key), item, key.label()
        return
    if not locations.is_struct(value):
        return
    for identifier, text, _prop in locations.struct_members(value, context):
        try:
            child = getattr(value, identifier)
        except AttributeError:
            continue
        yield at.extended(identifier), child, text


def _plain(target, value):
    prop = target.final_step().prop
    try:
        return _value_text(prop, value)
    except (TypeError, ValueError, AttributeError):
        return str(value)


def wrapped(text, width=40):
    return textwrap.wrap(text, width)


# -----------------------------------------------------------------------------
# Texts
# -----------------------------------------------------------------------------


def _icon(value):
    """The icon of a data-block's type (Object, Mesh, ...), else none."""
    icon = getattr(getattr(value, "bl_rna", None), "icon", "NONE")
    return None if icon in {"NONE", "DOT"} else icon


def _summary(value) -> str:
    """Short description of a pointer's or collection's current value."""
    if value is None:
        return "None"
    if locations.is_collection(value) or isinstance(value, list):
        count = len(value)
        return "1 item" if count == 1 else f"{count} items"
    name = getattr(value, "name", None)
    if isinstance(name, str) and name:
        return name
    return getattr(getattr(value, "bl_rna", None), "name", "")


def _kind(value, identifier):
    """POINTER / COLLECTION / VALUE of a context member."""
    current = getattr(value, identifier, None)
    if locations.is_collection(current) or isinstance(current, list):
        return "COLLECTION"
    if locations.is_struct(current) or identifier in rna.CONTEXT_MEMBERS:
        return "POINTER"
    return "VALUE"


def _value_text(prop, value) -> str:
    """A value as short text: `0.1 m`, `30°`, `Edges`, `On`, `(0, 0, 1)`."""
    if prop is None:
        return str(value)
    if prop.type == "ENUM":
        if prop.is_enum_flag:
            return ", ".join(_enum_name(prop, v) for v in sorted(value)) or "None"
        return _enum_name(prop, value)
    if prop.type == "STRING":
        return value if len(value) <= 40 else value[:39] + "…"
    size = _array_size(prop)
    if size:
        if size > MAX_ARRAY:
            return f"{size} values"
        return "(" + ", ".join(_number(prop, v) for v in value) + ")"
    return _number(prop, value)


def _number(prop, value) -> str:
    if isinstance(value, bool):
        return "On" if value else "Off"
    if isinstance(value, float):
        if prop.unit == "ROTATION":
            return f"{math.degrees(value):.4g}°"
        if prop.unit not in {"NONE", ""}:
            try:
                return bpy.utils.units.to_string(
                    bpy.context.scene.unit_settings.system,
                    prop.unit,
                    value,
                    precision=3,
                )
            except (ValueError, TypeError):
                pass
        return f"{value:.4g}"
    return str(value)


def _enum_name(prop, identifier) -> str:
    item = prop.enum_items.get(identifier)
    return item.name if item is not None else str(identifier)


def _array_size(prop) -> int:
    dimensions = [d for d in getattr(prop, "array_dimensions", ()) if d]
    size = 1
    for dimension in dimensions:
        size *= dimension
    return size if dimensions else 0


def register():
    bpy.types.WindowManager.sna_browser = bpy.props.PointerProperty(
        type=SNA_BrowserState
    )


def unregister():
    del bpy.types.WindowManager.sna_browser
