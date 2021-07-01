import bpy


class SN_PT_AddonSettingsPanel(bpy.types.Panel):
    bl_idname = "SN_PT_AddonSettingsPanel"
    bl_label = "Settings"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Serpens"
    bl_options = {"DEFAULT_CLOSED"}
    bl_order = 5

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
        row.label(text="Last Compile: "+addon_graph.last_compile_time)

        layout.prop(addon_graph, "compile_on_start", text="Compile on Startup")

        layout.separator()

        layout.prop(addon_graph, "autocompile", text="Auto Compile")
        row = layout.row()
        row.enabled = addon_graph.autocompile
        row.prop(addon_graph, "autocompile_delay", text="Delay")

        layout.separator()

        col = layout.column()
        col.enabled = bpy.data.is_saved
        col.prop(context.scene.sn, "use_autosave")
        row = col.row()
        row.enabled = context.scene.sn.use_autosave
        row.prop(context.scene.sn, "autosave_delay")

        layout.separator()

        layout.template_ID(context.scene.sn, "easy_bpy",
                           open="text.open", text="Easy BPY")
