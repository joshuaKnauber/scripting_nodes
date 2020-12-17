import bpy



class SN_PT_AddonSettingsPanel(bpy.types.Panel):
    bl_idname = "SN_PT_AddonSettingsPanel"
    bl_label = "Settings"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Serpens"
    bl_options = {"DEFAULT_CLOSED"}
    bl_order = 4

    @classmethod
    def poll(cls, context):
        return context.scene.sn.editing_addon != "NONE" and context.space_data.tree_type == "ScriptingNodesTree"

    def draw(self, context):
        layout = self.layout

        addon_tree = context.scene.sn.addon_tree()
        addon_graph = addon_tree.sn_graphs[0]
        
        layout.use_property_split = True
        layout.use_property_decorate = False
        row = layout.row()
        row.alignment = "RIGHT"
        row.label(text=addon_graph.last_compile_time)
        layout.prop(addon_graph, "autocompile", text="Auto Compile")
        if addon_graph.autocompile:
            layout.prop(addon_graph, "autocompile_delay", text="Delay")
        layout.prop(addon_graph, "compile_on_start", text="Compile on Startup")