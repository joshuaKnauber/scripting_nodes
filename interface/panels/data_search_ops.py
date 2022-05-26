import bpy
from ...settings.data_properties import get_data_items, item_from_path, filter_items, filter_defaults



class SN_OT_ShowDataOverview(bpy.types.Operator):
    bl_idname = "sn.show_data_overview"
    bl_label = "Show Data Overview"
    bl_description = "Opens a window that shows a data overview"
    bl_options = {"REGISTER", "INTERNAL"}

    def execute(self, context):
        context.scene.sn.global_search_active = False
        for area in context.screen.areas:
            if area.type == "PREFERENCES":
                break
        else:
            bpy.ops.screen.userpref_show("INVOKE_DEFAULT")
        if not context.scene.sn.hide_preferences:
            context.scene.sn.hide_preferences = True
        return {"FINISHED"}




class SN_OT_ExitDataSearch(bpy.types.Operator):
    bl_idname = "sn.exit_search"
    bl_label = "Exit Data Search"
    bl_description = "Exits the data search mode"
    bl_options = {"REGISTER", "INTERNAL"}

    def execute(self, context):
        context.scene.sn.global_search_active = False
        context.scene.sn.hide_preferences = False
        return {"FINISHED"}


    
class SN_OT_ExpandData(bpy.types.Operator):
    bl_idname = "sn.expand_data"
    bl_label = "Expand Data"
    bl_description = "Loads the items for the given item"
    bl_options = {"REGISTER", "INTERNAL"}
    
    path: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context): 
        sn = context.scene.sn
        item = item_from_path(sn.data_items, self.path)
        item["expanded"] = not item["expanded"]
        if not item["properties"]:
            try:
                item["data"]
                item["properties"] = get_data_items(self.path, item["data"])
            except:
                item["has_properties"] = False
                item["expanded"] = False
                self.report({"ERROR"}, message="This data doesn't exist anymore!")
        return {"FINISHED"}



class SN_OT_FilterData(bpy.types.Operator):
    bl_idname = "sn.filter_data"
    bl_label = "Filter Data"
    bl_description = "Filters this items data"
    bl_options = {"REGISTER", "INTERNAL"}
    
    path: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    def update_filters(self, context):
        item = item_from_path(context.scene.sn.data_items, self.path)
        item["data_search"] = self.data_search
        item["data_filter"] = self.data_filter

    data_search: bpy.props.StringProperty(default="",
                                    options={"SKIP_SAVE", "HIDDEN", "TEXTEDIT_UPDATE"},
                                    update=update_filters)
    
    data_filter: bpy.props.EnumProperty(name="Type",
                                        options={"ENUM_FLAG"},
                                        description="Filter by data type",
                                        items=filter_items,
                                        default=filter_defaults,
                                        update=update_filters)

    def update_reset(self, context):
        if not self.reset:
            self["reset"] = True
            self.data_search = ""
            self.data_filter = filter_defaults
    
    reset: bpy.props.BoolProperty(name="Reset", default=True,
                                description="Reset the filters",
                                update=update_reset)

    def execute(self, context):
        return {"FINISHED"}
    
    def draw(self, context):
        layout = self.layout
        layout.label(text="Search:")
        row = layout.row()
        row.prop(self, "data_search", text="")
        row.prop(self, "reset", text="", icon="LOOP_BACK", invert_checkbox=True)
        layout.separator()
        col = layout.column()
        col.prop(self, "data_filter", expand=True)
    
    def invoke(self, context, event):
        item = item_from_path(context.scene.sn.data_items, self.path)
        last_filter = item["data_filter"]
        last_search = item["data_search"]
        self.data_filter = last_filter
        self.data_search = last_search
        return context.window_manager.invoke_popup(self, width=300)
    
    

class SN_OT_ResetFilters(bpy.types.Operator):
    bl_idname = "sn.reset_filters"
    bl_label = "Reset Filters"
    bl_description = "Resets these filters"
    bl_options = {"REGISTER", "INTERNAL"}

    def execute(self, context):
        context.scene.sn.data_filter = filter_defaults
        context.scene.sn.data_search = ""
        for area in context.screen.areas:
            area.tag_redraw()
        return {"FINISHED"}



class SN_OT_ReloadData(bpy.types.Operator):
    bl_idname = "sn.reload_data"
    bl_label = "Reload Data"
    bl_description = "Reloads the listed scene data"
    bl_options = {"REGISTER", "INTERNAL"}

    def execute(self, context):
        context.scene.sn.global_search_active = False
        context.scene.sn.hide_preferences = True
        return {"FINISHED"}
    
    
    
class SN_OT_ResetItemFilters(bpy.types.Operator):
    bl_idname = "sn.reset_item_filters"
    bl_label = "Reset Item Filters"
    bl_description = "Reset this items filters"
    bl_options = {"REGISTER", "INTERNAL"}

    path: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        item = item_from_path(context.scene.sn.data_items, self.path)
        try:
            item["data"]
            item["data_filter"] = filter_defaults
            item["data_search"] = ""
        except:
            item["has_properties"] = False
            item["expanded"] = False
            self.report({"ERROR"}, message="This data doesn't exist anymore!")
        return {"FINISHED"}



class SN_OT_ReloadItemData(bpy.types.Operator):
    bl_idname = "sn.reload_item_data"
    bl_label = "Reload Item Data"
    bl_description = "Reloads this items data"
    bl_options = {"REGISTER", "INTERNAL"}

    path: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        item = item_from_path(context.scene.sn.data_items, self.path)
        try:
            item["data"]
            item["properties"] = get_data_items(self.path, item["data"])
        except:
            item["has_properties"] = False
            item["expanded"] = False
            self.report({"ERROR"}, message="This data doesn't exist anymore!")
        return {"FINISHED"}



class SN_OT_CopyDataPath(bpy.types.Operator):
    bl_idname = "sn.copy_data_path"
    bl_label = "Copy Data Path"
    bl_description = "Copy data path to paste in a node"
    bl_options = {"REGISTER", "INTERNAL"}

    path: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})
    type: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})
    required: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        context.window_manager.clipboard = self.path
        context.scene.sn.last_copied_datapath = self.path
        context.scene.sn.last_copied_datatype = self.type
        context.scene.sn.last_copied_required = self.required
        self.report({"INFO"}, message="Copied!")
        return {"FINISHED"}