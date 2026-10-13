"""The data explorer in the node editor's sidebar (Blend Data tab): the data
of the open file, one level at a time (blend_data/explorer.py).

With a Blender Data node active it shows where the node's path ends and
clicking an entry changes the path; otherwise it browses on its own and +
adds nodes.
"""

import bpy

from ...node_tree.editor import in_sn_tree
from .. import explorer, rna
from ..ops import explorer_location

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

    def draw_header_preset(self, context):
        self.layout.prop(
            context.scene.sna.ui, "explorer_follow", text="", icon="RESTRICT_SELECT_OFF"
        )

    def draw(self, context):
        layout = self.layout
        ui = context.scene.sna.ui
        node, location = explorer_location(context)
        if node is not None:
            row = layout.row()
            row.label(text=node.draw_label() or node.bl_label, icon="NODE")
        _draw_crumbs(layout, location, free=node is None)
        if not location.root:
            _draw_roots(layout)
            return
        layout.prop(ui, "explorer_filter", text="", icon="VIEWZOOM")
        _draw_location(layout.column(), context, location, node is not None)


def _draw_crumbs(layout, location, free):
    """Home, a back button named after the parent, and where you are (a full
    breadcrumb doesn't fit the sidebar)."""
    crumbs = location.crumbs()
    if free:
        crumbs.insert(0, ("Data", -1))
    row = layout.row(align=True)
    home = row.operator("sna.explorer_back", text="", icon="HOME")
    home.count = crumbs[0][1]
    if len(crumbs) > 1:
        parent, count = crumbs[-2]
        op = row.operator("sna.explorer_back", text=parent, icon="BACK")
        op.count = count
    row.label(text=crumbs[-1][0])


def _back(layout, text, count):
    op = layout.operator("sna.explorer_back", text=text, emboss=False)
    op.count = count


def _draw_roots(layout):
    col = layout.column(align=True)
    for root, text, icon in (
        ("CONTEXT", "Context", "WINDOW"),
        ("DATA", "Blend File", "FILE_BLEND"),
    ):
        row = col.row(align=True)
        op = row.operator("sna.explorer_open", text=text, icon=icon, emboss=False)
        op.root = root
        _target(row.operator("sna.explorer_add", text="", icon="ADD"), root=root)


def _draw_location(layout, context, location, following):
    """The entries at `location`; a plain value is shown in its owner's list."""
    try:
        value = explorer.evaluate(location, context)
    except explorer.Unavailable as error:
        layout.label(text=str(error), icon="INFO")
        _draw_static(layout, location)
        return
    highlight = None
    if not (explorer.is_struct(value) or explorer.is_collection(value)):
        if not location.parts:
            return
        highlight = location.parts[-1]
        location = location.truncated(len(location.parts) - 1)
        try:
            value = explorer.evaluate(location, context)
        except explorer.Unavailable:
            return
    search = context.scene.sna.ui.explorer_filter.lower()
    if explorer.is_collection(value):
        _draw_items(layout, value, location, search)
    elif explorer.is_struct(value):
        _draw_members(layout, context, value, search, following, highlight)


def _draw_members(layout, context, value, search, following, highlight):
    data, values = [], []
    for identifier, text, prop in explorer.struct_members(value, context):
        if search and search not in text.lower() and search not in identifier:
            continue
        kind = prop.type if prop is not None else _kind(value, identifier)
        (data if kind in {"POINTER", "COLLECTION"} else values).append(
            (identifier, text, prop, kind)
        )
    col = layout.column(align=True)
    for identifier, text, prop, kind in data:
        row = _row(col, identifier == highlight)
        try:
            current = getattr(value, identifier)
        except AttributeError:
            current = None
        row.active = current is not None
        op = _entry(row, text, _summary(current))
        op.member = identifier
        _target(row.operator("sna.explorer_add", text="", icon="ADD"), identifier)
    if data and values:
        layout.separator()
    col = layout.column(align=True)
    for identifier, text, prop, _kind_ in values:
        row = _row(col, identifier == highlight)
        if prop is None:
            row.label(text=f"{text}: {getattr(value, identifier, '')!s}")
        elif _array_size(prop) > MAX_ARRAY:
            row.label(text=f"{text} ({_array_size(prop)} values)")
        else:
            row.prop(value, identifier, text=text)
        if following:
            op = row.operator("sna.explorer_open", text="", icon="FORWARD")
            op.member = identifier
        _target(row.operator("sna.explorer_add", text="", icon="ADD"), identifier)
    if not data and not values:
        layout.label(text="Nothing found" if search else "No properties")


def _draw_items(layout, value, location, search):
    col = layout.column(align=True)
    active = getattr(value, "active", None)
    step = location.final_step()
    if active is not None and rna.member(step, "active").known:
        row = col.row(align=True)
        op = _entry(row, "Active", _summary(active))
        op.item_mode = "ACTIVE"
        _target(row.operator("sna.explorer_add", text="", icon="ADD"), mode="ACTIVE")
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
    if not step.known or not (step.rna_type or step.collection):
        return
    col = layout.column(align=True)
    if step.collection:
        _target(_entry(col.row(align=True), "First Item"), key=explorer.Key("INDEX", 0))
        return
    for member in rna.members(step):
        row = col.row(align=True)
        op = _entry(
            row, rna.label(member), rna.type_label(member), bool(member.rna_type)
        )
        op.member = member.name
        _target(row.operator("sna.explorer_add", text="", icon="ADD"), member.name)


# -----------------------------------------------------------------------------
# Helpers
# -----------------------------------------------------------------------------


def _entry(row, text, summary="", opens=True):
    """An entry: its name on the left (click to open), `summary` on the right.
    Returns the open operator."""
    left = row.row(align=True)
    left.alignment = "LEFT"
    icon = "RIGHTARROW_THIN" if opens else "DOT"
    op = left.operator("sna.explorer_open", text=text, icon=icon, emboss=False)
    right = row.row(align=True)
    right.alignment = "RIGHT"
    right.label(text=summary)
    return op


def _row(layout, highlight):
    if highlight:
        layout = layout.box()
    return layout.row(align=True)


def _target(op, member="", key=None, mode="", root=""):
    if root:
        op.root = root
    elif key is not None:
        op.item_mode = key.mode
        if key.mode == "NAME":
            op.item_name = key.value
        elif key.mode == "INDEX":
            op.item_index = key.value
    elif mode:
        op.item_mode = mode
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
        return str(len(value))
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
