"""Draws the path browser (blend_data/browser.py): a search over all paths,
or the columns of the path, each a scrolling list."""

import bpy

from .. import browser

WIDTH = 1000
ROWS = 18


class SNA_UL_BrowserEntries(bpy.types.UIList):
    bl_idname = "SNA_UL_BrowserEntries"

    def draw_item(self, context, layout, data, item, icon, active_data, active_prop):
        row = layout.row(align=True)
        row.label(text=item.name, icon=item.icon)
        right = row.row(align=True)
        right.alignment = "RIGHT"
        right.active = item.opens
        right.label(text=item.summary)
        if item.opens:
            right.label(icon="RIGHTARROW_THIN")


def draw(layout, context):
    state = context.window_manager.sna_browser
    layout.prop(
        state, "search", text="", icon="VIEWZOOM", placeholder="Search all paths"
    )
    if state.search.strip():
        _draw_results(layout, state)
        return
    here = browser.location(context)
    _draw_crumbs(layout, here)
    # equal widths: a row would size its columns by the rows in view, which
    # change when a list scrolls
    grid = layout.grid_flow(columns=browser.COLUMNS, even_columns=True)
    for index in range(browser.COLUMNS):
        col = grid.column()
        if index >= state.shown:
            continue
        slot = state.columns[index]
        col.label(text=slot.title)
        if slot.is_value:
            _draw_value(col, slot)
            continue
        if slot.note:
            col.label(text=slot.note, icon="INFO")
        col.template_list(
            SNA_UL_BrowserEntries.bl_idname,
            f"column_{index}",
            slot,
            "entries",
            slot,
            "active",
            rows=ROWS,
        )
    _draw_footer(layout, context, state, here)


def _draw_crumbs(layout, here):
    row = layout.row(align=True)
    row.alignment = "LEFT"
    crumbs = here.crumbs() if here.root else []
    for index, (text, count) in enumerate(crumbs):
        if index:
            row.label(icon="RIGHTARROW_THIN")
        op = row.operator("sna.browser_go", text=text, emboss=False)
        op.count = count
    if not crumbs:
        row.label(text="Pick where the path starts")


def _draw_value(col, slot):
    box = col.box()
    box.label(text=slot.value or "—")
    if slot.description:
        sub = col.column(align=True)
        sub.active = False
        for line in browser.wrapped(slot.description, 38):
            sub.label(text=line)


def _draw_footer(layout, context, state, here):
    row = layout.row()
    left = row.row()
    left.alignment = "LEFT"
    problem = browser.problem(context)
    if problem:
        left.alert = True
        left.label(text=problem, icon="ERROR")
    else:
        left.active = False
        left.label(text=code_path(here))
    right = row.row()
    right.alignment = "RIGHT"
    right.prop(state, "show_all")


def code_path(here) -> str:
    """The path as the generated code writes it (`data.` for the Data input)."""
    text = here.python()
    if here.root == "INPUT":
        return "data" + text.removeprefix("bpy.types").removeprefix(
            f".{here.input_type}"
        )
    return text.replace("bpy.context", "context")


def _draw_results(layout, state):
    layout.template_list(
        SNA_UL_BrowserEntries.bl_idname,
        "results",
        state,
        "results",
        state,
        "result_active",
        rows=ROWS,
    )
