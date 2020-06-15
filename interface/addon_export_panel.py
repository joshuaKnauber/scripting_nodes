import bpy


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
        """
        tree = context.space_data.node_tree
        name = tree.addon_name.lower().replace(" ","_") + ".py"
        text = True
        try:
            bpy.data.texts[name]
        except:
            text = False
        if text:
            row = layout.row()
            row.scale_y = 1.5
            row.operator("scripting_nodes.export_addon", text="Export addon",icon="EXPORT")
        else:
            layout.label(text="Reload the addon before exporting!")
        """
