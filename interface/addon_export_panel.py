import bpy
from ..compile.compiler import compiler


class SN_PT_ExportPanel(bpy.types.Panel):
    """Creates a panel that lets you export the addon and the current NodeTree"""
    bl_label = "Export"
    bl_order = 0
    bl_idname = "SN_PT_ExportPanel"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Visual Scripting"
    bl_options = {'DEFAULT_CLOSED'}

    @classmethod
    def poll(cls, context):
        if context.space_data.tree_type == 'ScriptingNodesTree':
            return context.space_data.node_tree != None

    def draw(self, context):
        layout = self.layout
        if compiler().is_active_compiled():
            col = layout.column(align=True)
            row = col.row(align=True)
            row.scale_y = 1.5
            row.operator("scripting_nodes.export_addon", text="Export addon",icon="EXPORT")
            row = col.row(align=True)
            row.operator("scripting_nodes.export_to_marketplace", text="Add to marketplace",icon="UGLYPACKAGE")
        else:
            layout.label(text="Compile the addon before exporting!")