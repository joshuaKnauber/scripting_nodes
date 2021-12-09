import bpy



class SN_PT_SnippetPanel(bpy.types.Panel):
    bl_idname = "SN_PT_SnippetPanel"
    bl_label = "Snippets"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Serpens"
    bl_order = 5
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == "ScriptingNodesTree" and context.space_data.node_tree

    def draw(self, context):
        layout = self.layout

        # snippets could now in theory start from any node because they all store their code
        # only issue is that they don't have controllable inputs and values but maybe those can only exist if you export a function
        if not context.active_node:
            layout.label(text="No node starting point selected", icon="ERROR")

        else:
            layout.operator("")