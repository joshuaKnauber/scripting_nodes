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
        row = layout.row(align=True)
        row.template_ID(context.scene.sn, "easy_bpy", open="text.open", text="Easy BPY")
        row.operator("wm.url_open", text="", icon="URL").url = "https://curtisholt.online/easybpy"

        layout.separator()
        col = layout.column(heading="Debug")
        col.prop(sn, "debug_python_nodes")
        col.prop(sn, "debug_python_sockets")