import bpy

from ._sn_helpers import sn_report, sn_write_text
from .scripts import toolkit_helpers


class OBJECT_TOOLKIT_OT_rename_selected(bpy.types.Operator):
    bl_idname = "object_toolkit.rename_selected"
    bl_label = "Rename Selected"
    bl_description = "Rename the selected objects with a prefix and a number"
    bl_options = {"REGISTER", "UNDO"}
    prefix: bpy.props.StringProperty(name="Prefix", default="Object")
    start: bpy.props.IntProperty(name="Start", default=1)

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        for index, item in enumerate(context.selected_objects):
            item.name = f"{self.prefix}_{index + self.start:03}"
        sn_report(self, "INFO", f"Renamed {len(context.selected_objects)} objects")
        return {"FINISHED"}


class OBJECT_TOOLKIT_OT_distribute(bpy.types.Operator):
    bl_idname = "object_toolkit.distribute"
    bl_label = "Distribute"
    bl_description = "Place the selected objects in a line"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        for index_2, item_2 in enumerate(context.selected_objects):
            item_2.location = (
                index_2 * context.scene.object_toolkit.spacing
                if context.scene.object_toolkit.axis == "X"
                else 0.0,
                index_2 * context.scene.object_toolkit.spacing
                if context.scene.object_toolkit.axis == "Y"
                else 0.0,
                index_2 * context.scene.object_toolkit.spacing
                if context.scene.object_toolkit.axis == "Z"
                else 0.0,
            )
        return {"FINISHED"}


class OBJECT_TOOLKIT_OT_save_selection_set(bpy.types.Operator):
    bl_idname = "object_toolkit.save_selection_set"
    bl_label = "Save Selection Set"
    bl_description = "Remember the selected objects as a set"
    bl_options = {"REGISTER", "UNDO"}
    name: bpy.props.StringProperty(name="Name", default="Set")

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self)

    def execute(self, context):
        item_3 = context.scene.object_toolkit.sets.add()
        item_3.name = self.name
        item_3.objects = ",".join(
            str(i) for i in [obj.name for obj in context.selected_objects]
        )
        return {"FINISHED"}


class OBJECT_TOOLKIT_OT_restore_selection_set(bpy.types.Operator):
    bl_idname = "object_toolkit.restore_selection_set"
    bl_label = "Restore Selection Set"
    bl_description = "Select the objects of the active set"
    bl_options = {"REGISTER", "UNDO"}

    def execute(self, context):
        count = toolkit_helpers.select_objects(
            names=context.scene.object_toolkit.sets[
                context.scene.object_toolkit.active_set
            ].objects
        )
        sn_report(self, "INFO", f"Selected {count} objects")
        return {"FINISHED"}


class OBJECT_TOOLKIT_OT_export_names(bpy.types.Operator):
    bl_idname = "object_toolkit.export_names"
    bl_label = "Export Names"
    bl_description = "Write the names of the selected objects to a file"
    bl_options = {"REGISTER", "UNDO"}
    filepath: bpy.props.StringProperty(
        subtype="FILE_PATH", options={"HIDDEN", "SKIP_SAVE"}
    )
    filter_glob: bpy.props.StringProperty(default="*.txt", options={"HIDDEN"})
    check_existing: bpy.props.BoolProperty(default=True, options={"HIDDEN"})

    def invoke(self, context, event):
        context.window_manager.fileselect_add(self)
        return {"RUNNING_MODAL"}

    def execute(self, context):
        sn_write_text(
            self.filepath,
            "\n".join(str(i) for i in [obj.name for obj in context.selected_objects]),
        )
        sn_report(self, "INFO", f"Wrote {self.filepath}")
        return {"FINISHED"}


class OBJECT_TOOLKIT_OT_measure(bpy.types.Operator):
    bl_idname = "object_toolkit.measure"
    bl_label = "Measure"
    bl_description = "Show the mouse position in the header"
    bl_options = {"REGISTER", "UNDO"}

    def invoke(self, context, event):
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}

    def modal(self, context, event):
        result = self._modal(context, event)
        if result is None:
            return {"RUNNING_MODAL"}
        if not result & {"RUNNING_MODAL", "PASS_THROUGH"}:
            self._end(context)
        return result

    def _modal(self, context, event):
        if event.type in {"ESC", "RIGHTMOUSE"} and event.value == "PRESS":
            return {"CANCELLED"}
        if context.area:
            context.area.header_text_set(
                f"Mouse: {(event.mouse_region_x, event.mouse_region_y)}"
            )
        if event.type == "LEFTMOUSE" and event.value == "PRESS":
            return {"FINISHED"}

    def _end(self, context):
        if context.area:
            context.area.header_text_set(None)

    def cancel(self, context):
        self._end(context)
