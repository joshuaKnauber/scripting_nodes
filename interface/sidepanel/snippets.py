import bpy

        
class SN_PT_SnippetPanel(bpy.types.Panel):
    bl_idname = "SN_PT_SnippetPanel"
    bl_label = "Snippets [BETA]"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Serpens"
    bl_order = 4
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        return context.scene.sn.editing_addon != "NONE" and context.space_data.tree_type == "ScriptingNodesTree" and context.space_data.node_tree

    def draw(self, context):
        layout = self.layout

        node = context.space_data.node_tree.nodes.active
        if node and node.bl_idname == "SN_RunFunctionNode":
            if not context.scene.sn.active_addon_has_changes():
                row = layout.row()
                row.scale_y = 1.25
                row.operator("sn.save_snippet",icon="EXPORT")
            else:
                layout.label(text="Compile addon to save snippet",icon="INFO")
        else:
            layout.label(text="Select Run Function node to create snippet",icon="INFO")