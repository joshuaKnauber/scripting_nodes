import bpy



class SN_OT_ShowDataOverview(bpy.types.Operator):
    bl_idname = "sn.show_data_overview"
    bl_label = "Show Data Overview"
    bl_description = "Opens a window that shows a data overview"
    bl_options = {"REGISTER", "INTERNAL"}

    def execute(self, context):
        for area in context.screen.areas:
            if area.type == "PREFERENCES":
                break
        else:
            bpy.ops.screen.userpref_show("INVOKE_DEFAULT")
        context.scene.sn.hide_preferences = True
        return {"FINISHED"}




class SN_OT_ExitDataSearch(bpy.types.Operator):
    bl_idname = "sn.exit_search"
    bl_label = "Exit Data Search"
    bl_description = "Exits the data search mode"
    bl_options = {"REGISTER", "INTERNAL"}

    def execute(self, context):
        context.scene.sn.hide_preferences = False
        return {"FINISHED"}



class SN_OT_ReloadData(bpy.types.Operator):
    bl_idname = "sn.reload_data"
    bl_label = "Reload Data"
    bl_description = "Reloads the listed scene data"
    bl_options = {"REGISTER", "INTERNAL"}

    def execute(self, context):
        context.scene.sn.hide_preferences = True
        return {"FINISHED"}



class SN_OT_ReloadItemData(bpy.types.Operator):
    bl_idname = "sn.reload_item_data"
    bl_label = "Reload ItemData"
    bl_description = "Reloads this items data"
    bl_options = {"REGISTER", "INTERNAL"}

    path: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        for item in context.scene.sn.data_items:
            if item.path == self.path:
                item.reload_items()
                break
        return {"FINISHED"}