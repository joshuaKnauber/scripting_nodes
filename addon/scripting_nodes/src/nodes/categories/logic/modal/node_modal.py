"""Nodes for modal operators (Operator node, Invoke Type Modal): ending the
operator, checking events, text in the header and status bar, the cursor."""

import bpy

from .....blend_data.rna import blend_data_spec
from .....core.context import NodeError
from .....sockets.spec import Boolean, Flow, String
from ....base_node import ScriptingBaseNode
from ..node_operator import CURSORS
from ..node_shortcut import KEYS

RETURNS = [
    ("FINISHED", "Finish", "End the operator, keep what it did (an undo step)"),
    ("CANCELLED", "Cancel", "End the operator, as if it didn't run"),
    (
        "PASS_THROUGH",
        "Pass Through",
        "Modal: let Blender handle this event too (e.g. to navigate the view)",
    ),
    ("RUNNING_MODAL", "Keep Running", "Modal: skip the rest, wait for the next event"),
]


class SNA_Node_OperatorReturn(ScriptingBaseNode, bpy.types.Node):
    """End an operator's flow early: finish, cancel, or (in a modal
    operator) pass the event on or wait for the next one."""

    bl_idname = "SNA_Node_OperatorReturn"
    bl_label = "Return"
    sn_inputs = [Flow()]
    sn_header_props = ("result",)

    result: bpy.props.EnumProperty(name="Result", items=RETURNS)

    def draw_label(self):
        return next(label for key, label, _ in RETURNS if key == self.result)

    def emit(self, ctx):
        ctx.code(f"return {{{self.result!r}}}")


class SNA_Node_IsKey(ScriptingBaseNode, bpy.types.Node):
    """Whether an event is a key or mouse button, e.g. Left Mouse pressed."""

    bl_idname = "SNA_Node_IsKey"
    bl_label = "Is Key"
    sn_inputs = [blend_data_spec("event", "Event", "Event")]
    sn_outputs = [Boolean("is_key", "Is Key")]
    sn_header_props = ("key", "value")

    key: bpy.props.EnumProperty(name="Key", items=KEYS, default="LEFTMOUSE")
    value: bpy.props.EnumProperty(
        name="Event",
        items=[
            ("PRESS", "Press", "When it's pressed"),
            ("RELEASE", "Release", "When it's released"),
            ("ANY", "Any", "Pressed or released"),
        ],
    )

    def emit(self, ctx):
        if not ctx.is_linked("event") and "event" not in ctx.scope.names:
            raise NodeError("Connect an event (the Operator's Event output)")
        event = ctx.input("event", default="event")
        check = f"{event}.type == {self.key!r}"
        if self.value != "ANY":
            check += f" and {event}.value == {self.value!r}"
        ctx.output("is_key", check)


def _text_or_none(node, ctx):
    """The text, None (Blender's own text again) when it's empty."""
    text = node.socket("text")
    if not text.is_linked:
        return repr(text.value) if text.value else "None"
    return f"{ctx.input('text')} or None"


class SNA_Node_SetHeaderText(ScriptingBaseNode, bpy.types.Node):
    """Show text in the editor's header instead of its menus (empty text:
    the menus again), e.g. what a modal operator does."""

    bl_idname = "SNA_Node_SetHeaderText"
    bl_label = "Set Header Text"
    sn_inputs = [Flow(), String("text", "Text")]
    sn_outputs = [Flow("next")]

    def emit(self, ctx):
        ctx.code(f"""
            if {ctx.context}.area:
                {ctx.context}.area.header_text_set({_text_or_none(self, ctx)})
            {ctx.flow("next")}
        """)


class SNA_Node_SetStatusText(ScriptingBaseNode, bpy.types.Node):
    """Show text in the status bar (empty text: Blender's own again), e.g.
    the keys a modal operator reacts to."""

    bl_idname = "SNA_Node_SetStatusText"
    bl_label = "Set Status Text"
    sn_inputs = [Flow(), String("text", "Text")]
    sn_outputs = [Flow("next")]

    def emit(self, ctx):
        ctx.code(f"""
            {ctx.context}.workspace.status_text_set({_text_or_none(self, ctx)})
            {ctx.flow("next")}
        """)


class SNA_Node_SetCursor(ScriptingBaseNode, bpy.types.Node):
    """Change the mouse cursor until it's set back (Default), e.g. while a
    modal operator runs."""

    bl_idname = "SNA_Node_SetCursor"
    bl_label = "Set Cursor"
    sn_inputs = [Flow()]
    sn_outputs = [Flow("next")]
    sn_header_props = ("cursor",)

    cursor: bpy.props.EnumProperty(name="Cursor", items=CURSORS, default="CROSSHAIR")

    def emit(self, ctx):
        window = f"{ctx.context}.window"
        if self.cursor == "DEFAULT":
            call = f"{window}.cursor_modal_restore()"
        else:
            call = f"{window}.cursor_modal_set({self.cursor!r})"
        ctx.code(f"""
            if {window}:
                {call}
            {ctx.flow("next")}
        """)
