import bpy

from .....lib.trees import node_by_id

# keys that only modify the shortcut, or aren't keys at all
_IGNORED = {
    "LEFT_CTRL", "RIGHT_CTRL", "LEFT_SHIFT", "RIGHT_SHIFT", "LEFT_ALT",
    "RIGHT_ALT", "OSKEY", "MOUSEMOVE", "INBETWEEN_MOUSEMOVE", "TIMER",
    "TIMER_REPORT", "TIMER_REGION", "WINDOW_DEACTIVATE", "NONE",
}  # fmt: skip


class SNA_OT_RecordShortcut(bpy.types.Operator):
    bl_idname = "sna.record_shortcut"
    bl_label = "Record Shortcut"
    bl_description = "Press the keys of the shortcut (Esc cancels)"
    bl_options = {"INTERNAL"}

    node_id: bpy.props.StringProperty(options={"HIDDEN"})

    def invoke(self, context, event):
        if node_by_id(self.node_id) is None:
            return {"CANCELLED"}
        context.window_manager.modal_handler_add(self)
        context.workspace.status_text_set("Press the shortcut, Esc to cancel")
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        if event.type in _IGNORED or event.value != "PRESS":
            return {"RUNNING_MODAL"}
        context.workspace.status_text_set(None)
        if event.type == "ESC":
            return {"CANCELLED"}
        node = node_by_id(self.node_id)
        if node is None:
            return {"CANCELLED"}
        node.key = event.type
        node.ctrl, node.shift = event.ctrl, event.shift
        node.alt, node.oskey = event.alt, event.oskey
        if context.area:
            context.area.tag_redraw()
        return {"FINISHED"}
