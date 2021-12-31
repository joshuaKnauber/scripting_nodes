import bpy



class SN_PT_AddonSettingsPanel(bpy.types.Panel):
    bl_idname = "SN_PT_AddonSettingsPanel"
    bl_label = "Settings"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Serpens"
    bl_options = {"DEFAULT_CLOSED"}
    bl_order = 6

    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == "ScriptingNodesTree" and context.space_data.node_tree

    def draw(self, context):
        layout = self.layout
        sn = context.scene.sn

        layout.use_property_split = True
        layout.use_property_decorate = False

        col = layout.column(heading="General")
        col.prop(sn, "compile_on_load")

        layout.separator()
        col = layout.column(heading="Debug")
        col.prop(sn, "debug_python_nodes")
        col.prop(sn, "debug_python_sockets")
        col.prop(sn, "debug_python_properties")
        col.prop(sn, "debug_code")
        
        
        
class SN_PT_EasyBpyPanel(bpy.types.Panel):
    bl_idname = "SN_PT_EasyBpyPanel"
    bl_parent_id = "SN_PT_AddonSettingsPanel"
    bl_label = "Easy BPY"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Serpens"
    bl_order = 0

    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == "ScriptingNodesTree" and context.space_data.node_tree

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
