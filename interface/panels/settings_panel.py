import bpy


class SN_PT_SettingsPanel(bpy.types.Panel):
    bl_idname = "SN_PT_SettingsPanel"
    bl_label = "Settings"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Serpens"
    bl_options = {"DEFAULT_CLOSED"}
    bl_order = 4

    @classmethod
    def poll(cls, context):
        return (
            context.space_data.tree_type == "ScriptingNodesTree"
            and context.space_data.node_tree
        )

    def draw(self, context):
        layout = self.layout
        sn = context.scene.sn

        layout.use_property_split = True
        layout.use_property_decorate = False

        # col = layout.column(heading="General")
        # col.prop(sn, "compile_on_load")

        layout.separator()
        col = layout.column(heading="Debug")
        col.prop(sn, "dev_logs")
        # col.prop(sn, "debug_compile_time", text="Log Compile Time")
        # col.prop(sn, "debug_python_nodes")
        # col.prop(sn, "debug_python_sockets")
        # subrow = col.row()
        # subrow.active = sn.debug_python_nodes or sn.debug_python_sockets
        # subrow.prop(sn, "debug_selected_only")
