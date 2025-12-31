import bpy
from scripting_nodes.src.lib.editor.editor import in_sn_tree
from scripting_nodes.src.features.blend_data import BlendDataIndex


class SNA_OT_CopyPropertyPath(bpy.types.Operator):
    """Copy property path to clipboard"""

    bl_idname = "sna.copy_property_path"
    bl_label = "Copy Property Path"
    bl_options = {"REGISTER"}

    path: bpy.props.StringProperty()

    def execute(self, context):
        context.window_manager.clipboard = self.path
        self.report({"INFO"}, f"Copied: {self.path}")
        return {"FINISHED"}


class SNA_OT_CopyPropertyPathMenu(bpy.types.Operator):
    """Choose which property path to copy"""

    bl_idname = "sna.copy_property_path_menu"
    bl_label = "Copy Property Path"
    bl_options = {"REGISTER"}
    bl_property = "path_enum"

    property_key: bpy.props.StringProperty()

    def get_path_items(self, context):
        index = BlendDataIndex()
        if self.property_key in index.properties:
            prop_info = index.properties[self.property_key]
            return [(p, p, "") for p in prop_info.access_paths]
        return []

    path_enum: bpy.props.EnumProperty(
        name="Path",
        items=get_path_items,
    )

    def execute(self, context):
        context.window_manager.clipboard = self.path_enum
        self.report({"INFO"}, f"Copied: {self.path_enum}")
        return {"FINISHED"}

    def invoke(self, context, event):
        context.window_manager.invoke_search_popup(self)
        return {"FINISHED"}


class SNA_PT_BlendData(bpy.types.Panel):
    bl_idname = "SNA_PT_BlendData"
    bl_label = "Blend Data"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Scripting Nodes"
    bl_options = {"DEFAULT_CLOSED"}
    bl_order = 4

    @classmethod
    def poll(cls, context):
        return in_sn_tree(context)

    def draw(self, context):
        layout = self.layout
        ui = context.scene.sna.ui
        index = BlendDataIndex()

        # Not indexed yet - show big index button
        if not index.is_indexed:
            layout.separator()
            col = layout.column()
            col.scale_y = 1.5
            col.operator(
                "sna.index_blend_data", text="Index Blend Data", icon="ZOOM_ALL"
            )
            layout.separator()
            box = layout.box()
            col = box.column(align=True)
            col.label(text="Scan all available Blender", icon="INFO")
            col.label(text="properties for quick access")
            return

        # Indexed - show search and list
        row = layout.row(align=True)
        row.prop(ui, "blend_data_search", text="", icon="VIEWZOOM")
        row.operator("sna.index_blend_data", text="", icon="FILE_REFRESH")
        row.operator("sna.paste_blend_data_path", text="", icon="PASTEDOWN")

        search_term = ui.blend_data_search
        results = index.search(search_term, max_results=25)

        if not results:
            box = layout.box()
            box.label(text="No results found", icon="INFO")
            return

        # Group results by RNA type
        grouped: dict[str, list] = {}
        for prop_info, score in results:
            rna_type = prop_info.rna_type
            if rna_type not in grouped:
                grouped[rna_type] = []
            grouped[rna_type].append((prop_info, score))

        # Draw results grouped by type
        for rna_type, props in grouped.items():
            box = layout.box()
            col = box.column(align=True)

            # Type header
            header = col.row()
            header.label(text=rna_type, icon="RNA")

            # Properties in this type
            for prop_info, score in props:
                row = col.row(align=True)

                # Property name
                row.label(text=prop_info.name)

                # Property type (dimmed)
                sub = row.row()
                sub.active = False
                sub.label(text=prop_info.type_name)

                # Copy button
                if len(prop_info.access_paths) == 1:
                    op = row.operator(
                        "sna.copy_property_path", text="", icon="COPYDOWN"
                    )
                    op.path = prop_info.access_paths[0]
                else:
                    op = row.operator(
                        "sna.copy_property_path_menu", text="", icon="DOWNARROW_HLT"
                    )
                    op.property_key = prop_info.unique_key
