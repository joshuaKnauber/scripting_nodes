import bpy


class SN_PT_FilesPanel(bpy.types.Panel):
    bl_idname = "SN_PT_FilesPanel"
    bl_label = "Files"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Serpens"
    bl_order = 1
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        return (
            context.space_data.tree_type == "ScriptingNodesTree"
            and context.space_data.node_tree
            and context.scene.sn.use_addon
        )

    def draw_header(self, context):
        layout = self.layout
        sn = context.scene.sn
        layout.prop(sn, "use_files", text="")
        layout.separator(factor=0.25)

    def draw(self, context):
        layout = self.layout
        layout.enabled = context.scene.sn.use_files
        sn = context.scene.sn

        col = layout.column(align=True)
        box = col.box()
        row = box.row()
        row.scale_y = 0.9
        row.alignment = "RIGHT"

        subrow = row.row()
        subrow.enabled = sn.active_file != None
        subrow.operator(
            "sn.create_folder", text="", icon="FILE_NEW", emboss=False
        ).path = (sn.active_file.path if sn.active_file else "")
        subrow.operator(
            "sn.create_folder", text="", icon="NEWFOLDER", emboss=False
        ).path = (sn.active_file.path if sn.active_file else "")
        row.separator()

        row.operator("sn.reload_files", text="", icon="FILE_REFRESH", emboss=False)
        subcol = row.column(align=True)
        subcol.scale_x = 1.2
        subcol.popover(
            panel="SN_PT_FileSettingsPanel",
            text="",
            icon="FILE_FOLDER",
        )

        col.template_list(
            "SN_FILES_UL_items",
            "",
            context.scene.sn,
            "file_list",
            context.scene.sn,
            "active_file_index",
            rows=5,
        )
