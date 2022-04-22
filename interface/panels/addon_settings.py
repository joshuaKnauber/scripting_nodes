import bpy



class SN_PT_AddonSettingsPanel(bpy.types.Panel):
    bl_idname = "SN_PT_AddonSettingsPanel"
    bl_label = ""
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Serpens"
    bl_options = {"DEFAULT_CLOSED", "HEADER_LAYOUT_EXPAND"}
    bl_order = 7

    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == "ScriptingNodesTree" and context.space_data.node_tree
    
    def draw_header(self, context):
        layout = self.layout
        layout.label(text="Settings")
        layout.operator("wm.url_open", text="", icon="QUESTION", emboss=False).url = "https://joshuaknauber.notion.site/Workflow-Introduction-d235d03178124dc9b752088d75a25192"

    def draw(self, context):
        layout = self.layout
        sn = context.scene.sn

        layout.use_property_split = True
        layout.use_property_decorate = False

        col = layout.column(heading="General")
        col.prop(sn, "compile_on_load")

        layout.separator()
        col = layout.column(heading="Debug")
        col.prop(sn, "debug_compile_time")
        col.prop(sn, "debug_python_nodes")
        col.prop(sn, "debug_python_sockets")
        col.prop(sn, "debug_python_properties")
        col.prop(sn, "debug_code")
        sub_row = col.row()
        sub_row.enabled = sn.debug_code
        sub_row.prop(sn, "format_code")
        
        
        
class SN_PT_EasyBpyPanel(bpy.types.Panel):
    bl_idname = "SN_PT_EasyBpyPanel"
    bl_parent_id = "SN_PT_AddonSettingsPanel"
    bl_label = ""
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Serpens"
    bl_order = 0
    bl_options={"HEADER_LAYOUT_EXPAND"}

    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == "ScriptingNodesTree" and context.space_data.node_tree
    
    def draw_header(self, context):
        layout = self.layout
        layout.label(text="Easy BPY")
        layout.operator("wm.url_open", text="", icon="QUESTION", emboss=False).url = "https://joshuaknauber.notion.site/Easy-BPY-e3a894c7bf4c469389e6caa7640c3219"

    def draw(self, context):
        layout = self.layout
        sn = context.scene.sn

        layout.use_property_split = True
        layout.use_property_decorate = False

        if sn.easy_bpy_path:
            layout.label(text="Easy BPY installed", icon="CHECKMARK")
            layout.operator("sn.open_explorer", text="Open Install", icon="FILE_FOLDER").path = sn.easy_bpy_path
        else:
            layout.label(text="Easy BPY not installed", icon="CANCEL")
        layout.operator("wm.url_open", text="Documentation", icon="URL").url = "https://curtisholt.online/easybpy"
