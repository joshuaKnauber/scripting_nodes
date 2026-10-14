"""Picker of the Add to Menu / Panel / Header nodes: draws a "Pick" entry into
every menu, panel or header; clicking one sets the node's target."""

import bpy

from .....lib.trees import node_by_id

_active_node_id = None
_picked_classes = []  # classes the pick entry is drawn into


def _draw_pick(self, context):
    name = type(self).__name__
    label = getattr(type(self), "bl_label", "") or name
    row = self.layout.row()
    row.alert = True
    op = row.operator(
        "sna.add_to_picker_select", text=f"Pick '{label}'", icon="EYEDROPPER"
    )
    op.target = f"{label}  [{name}]"


def is_active(node):
    return _active_node_id == node.id


def stop():
    global _active_node_id
    for cls in _picked_classes:
        try:
            cls.remove(_draw_pick)
        except Exception:
            pass
    _picked_classes.clear()
    _active_node_id = None
    for window in bpy.context.window_manager.windows:
        for area in window.screen.areas:
            area.tag_redraw()


class SNA_OT_AddToPickerStart(bpy.types.Operator):
    bl_idname = "sna.add_to_picker_start"
    bl_label = "Pick in the Interface"
    bl_description = "Pick the menu, panel or header to draw into in Blender's UI"
    bl_options = {"REGISTER", "INTERNAL"}

    node_id: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        global _active_node_id
        from ..node_add_to import classes

        node = node_by_id(self.node_id)
        if node is None:
            return {"CANCELLED"}
        stop()
        _active_node_id = node.id
        for _, name in classes(node.base):
            cls = getattr(bpy.types, name)
            try:
                cls.append(_draw_pick)
            except Exception:
                continue
            _picked_classes.append(cls)
        for area in context.screen.areas:
            area.tag_redraw()
        self.report({"INFO"}, f"Click 'Pick' in the {node.kind} to draw into")
        return {"FINISHED"}


class SNA_OT_AddToPickerSelect(bpy.types.Operator):
    bl_idname = "sna.add_to_picker_select"
    bl_label = "Pick"
    bl_description = "Draw the node's interface into this one"
    bl_options = {"REGISTER", "INTERNAL"}

    target: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        node = node_by_id(_active_node_id) if _active_node_id else None
        if node is not None:
            node.target = self.target
        stop()
        return {"FINISHED"}


class SNA_OT_AddToPickerCancel(bpy.types.Operator):
    bl_idname = "sna.add_to_picker_cancel"
    bl_label = "Cancel Picker"
    bl_description = "Stop picking"
    bl_options = {"REGISTER", "INTERNAL"}

    def execute(self, context):
        stop()
        return {"FINISHED"}


def unregister():
    stop()
