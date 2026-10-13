"""The data explorer in the node editor's sidebar (Blend Data tab): the data
of the open file, one level at a time (blend_data/explorer.py).

It's a browser: clicking only moves the explorer. Nodes change through +
(add a node) and the buttons for the selected node under the path.
"""

import bpy

from ...node_tree.editor import in_sn_tree
from .. import explorer, rna
from ..ops.explorer import location as explorer_location
from ..ops.explorer import selected_node

MAX_ITEMS = 50
# vectors up to this length are drawn as fields, longer arrays as a label
MAX_ARRAY = 4


class SNA_PT_DataExplorer(bpy.types.Panel):
    bl_idname = "SNA_PT_DataExplorer"
    bl_label = "Data Explorer"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Blend Data"

    @classmethod
    def poll(cls, context):
        return in_sn_tree(context)

    def draw(self, context):
        layout = self.layout
        ui = context.scene.sna.ui
        location = explorer_location(context)
        _draw_header(layout, location)
        _draw_selected_node(layout, context, location)
        if not location.root:
            _draw_roots(layout)
        else:
            layout.prop(ui, "explorer_filter", text="", icon="VIEWZOOM")
            _draw_location(layout, context, location)


def _draw_header(layout, location):
    """Where the explorer is: the path as code, back and home."""
    box = layout.box()
    path = location.python().replace("bpy.context", "context")
    box.label(text=path or "Context or Blend File")
    row = box.row(align=True)
    row.enabled = bool(location.root)
    back = row.operator("sna.explorer_back", text="Back", icon="BACK")
    back.count = len(location.parts) - 1 if location.parts else -1
    home = row.operator("sna.explorer_back", text="", icon="HOME")
    home.count = -1


def _draw_roots(layout):
    col = layout.column(align=True)
    for root, text, icon, description in (
        ("CONTEXT", "Context", "WINDOW", "active object, scene, ..."),
        ("DATA", "Blend File", "FILE_BLEND", "all objects, materials, ..."),
    ):
        _target(_entry(col.row(align=True), text, description, icon=icon), root=root)


def _draw_location(layout, context, location):
    """The entries at `location`; a plain value is shown in its owner's list."""
    try:
        value = explorer.evaluate(location, context)
    except explorer.Unavailable as error:
        layout.label(text=f"{error}, showing what could be there", icon="INFO")
        _draw_static(layout, location)
        return
    highlight = None
    if not (explorer.is_struct(value) or explorer.is_collection(value)):
        if not location.parts:
            return
        highlight = location.parts[-1]
        owner = location.truncated(len(location.parts) - 1)
        try:
            value = explorer.evaluate(owner, context)
        except explorer.Unavailable:
            return
    ui = context.scene.sna.ui
    search = ui.explorer_filter.lower()
    if explorer.is_collection(value):
        _draw_items(layout, value, location, search)
    else:
        _draw_members(layout, context, value, search, ui.explorer_show_all, highlight)


def _draw_members(layout, context, value, search, show_all, highlight):
    data, values, hidden = [], [], 0
    for identifier, text, prop in explorer.struct_members(value, context):
        if search and search not in text.lower() and search not in identifier:
            continue
        kind = prop.type if prop is not None else _kind(value, identifier)
        try:
            current = getattr(value, identifier)
        except AttributeError:
            current = None
        if kind in {"POINTER", "COLLECTION"}:
            empty = current is None or (
                explorer.is_collection(current) and not len(current)
            )
            if empty and not show_all and identifier != highlight:
                hidden += 1
                continue
            data.append((identifier, text, current))
        else:
            internal = prop is None or prop.is_readonly
            if internal and not show_all and identifier != highlight:
                hidden += 1
                continue
            values.append((identifier, text, prop, current))

    if data:
        header, body = layout.panel("sna_explorer_data")
        header.label(text=f"Data ({len(data)})")
        if body is not None:
            col = body.column(align=True)
            for identifier, text, current in data:
                row = _row(col, identifier == highlight)
                row.active = current is not None
                _target(_entry(row, text, _summary(current)), identifier)
                _add(row, identifier)
    if values:
        header, body = layout.panel("sna_explorer_values")
        header.label(text=f"Values ({len(values)})")
        if body is not None:
            col = body.column(align=True)
            for identifier, text, prop, current in values:
                row = _row(col, identifier == highlight)
                if prop is None:
                    row.label(text=f"{text}: {current!s}")
                elif _array_size(prop) > MAX_ARRAY:
                    row.label(text=f"{text} ({_array_size(prop)} values)")
                else:
                    row.prop(value, identifier, text=text)
                _add(row, identifier)
    if not data and not values:
        layout.label(text="Nothing found" if search else "Nothing to show")
    if hidden or show_all:
        text = "Show Empty and Internal" + (f" ({hidden})" if hidden else "")
        layout.prop(context.scene.sna.ui, "explorer_show_all", text=text)


def _draw_items(layout, value, location, search):
    col = layout.column(align=True)
    active = getattr(value, "active", None)
    if active is not None and rna.member(location.final_step(), "active").known:
        row = col.row(align=True)
        _target(_entry(row, "Active", _summary(active)), "active")
        _add(row, "active")
        col.separator()
    shown = hidden = 0
    for index, item in enumerate(value):
        key = explorer.item_key(value, index, item)
        text = key.label()
        if search and search not in text.lower():
            continue
        if shown >= MAX_ITEMS:
            hidden += 1
            continue
        shown += 1
        row = col.row(align=True)
        _target(_entry(row, text), key=key)
        _target(row.operator("sna.explorer_add", text="", icon="ADD"), key=key)
    if hidden:
        col.label(text=f"{hidden} more, filter to find them")
    if not shown and not hidden:
        col.label(text="Nothing found" if search else "Empty")


def _draw_static(layout, location):
    """Without live data: the members of the type, no values."""
    step = location.final_step()
    if not step.known or step.collection or not step.rna_type:
        return
    col = layout.column(align=True)
    for member in rna.members(step):
        row = col.row(align=True)
        opens = bool(member.rna_type)
        _target(
            _entry(row, rna.label(member), rna.type_label(member), opens), member.name
        )
        _add(row, member.name)


def _draw_selected_node(layout, context, location):
    node = selected_node(context)
    if node is None:
        return
    box = layout.box()
    box.label(text=f"Selected: {node.draw_label() or node.bl_label}", icon="NODE")
    row = box.row(align=True)
    row.operator("sna.explorer_go_to_node", icon="ZOOM_SELECTED")
    sub = row.row(align=True)
    sub.enabled = bool(location.root)
    sub.operator("sna.explorer_use_for_node", icon="CHECKMARK")


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------


def _entry(row, text, summary="", opens=True, icon=None):
    """An entry: its name on the left (click to open), `summary` on the right.
    Returns the open operator."""
    left = row.row(align=True)
    left.alignment = "LEFT"
    icon = icon or ("RIGHTARROW_THIN" if opens else "DOT")
    op = left.operator("sna.explorer_open", text=text, icon=icon, emboss=False)
    right = row.row(align=True)
    right.alignment = "RIGHT"
    right.label(text=summary)
    return op


def _add(row, member):
    op = row.operator("sna.explorer_add", text="", icon="ADD")
    op.member = member


def _row(layout, highlight):
    if highlight:
        layout = layout.box()
    return layout.row(align=True)


def _target(op, member="", key=None, root=""):
    if root:
        op.root = root
    elif key is not None:
        op.item_mode = key.mode
        if key.mode == "NAME":
            op.item_name = key.value
        else:
            op.item_index = key.value
    else:
        op.member = member


def _kind(value, identifier):
    """POINTER / COLLECTION / VALUE of a context member."""
    current = getattr(value, identifier, None)
    if explorer.is_collection(current) or isinstance(current, list):
        return "COLLECTION"
    if explorer.is_struct(current) or identifier in rna.CONTEXT_MEMBERS:
        return "POINTER"
    return "VALUE"


def _summary(value) -> str:
    """Short description of a pointer's or collection's current value."""
    if value is None:
        return "None"
    if explorer.is_collection(value) or isinstance(value, list):
        return f"{len(value)} items"
    name = getattr(value, "name", None)
    if isinstance(name, str) and name:
        return name
    return getattr(getattr(value, "bl_rna", None), "name", "")


def _array_size(prop) -> int:
    dimensions = [d for d in getattr(prop, "array_dimensions", ()) if d]
    size = 1
    for dimension in dimensions:
        size *= dimension
    return size if dimensions else 0
