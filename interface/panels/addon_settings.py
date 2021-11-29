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

        layout.prop(sn, "debug_python_nodes")
        layout.prop(sn, "debug_python_sockets")

        # layout.prop(addon_graph, "compile_on_start", text="Compile on Startup")

        # layout.separator()

        # layout.template_ID(context.scene.sn, "easy_bpy",
        #                    open="text.open", text="Easy BPY")