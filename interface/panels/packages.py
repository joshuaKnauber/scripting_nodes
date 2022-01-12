import bpy



class SN_PT_PackagesPanel(bpy.types.Panel):
    bl_idname = "SN_PT_PackagesPanel"
    bl_label = "Packages"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Serpens"
    bl_order = 6
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == "ScriptingNodesTree" and context.space_data.node_tree

    def draw(self, context):
        layout = self.layout
        
        
        
class SN_PT_PackageDevPanel(bpy.types.Panel):
    bl_idname = "SN_PT_PackageDevPanel"
    bl_parent_id = "SN_PT_PackagesPanel"
    bl_label = "Development"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Serpens"
    bl_order = 0
    bl_options = {"DEFAULT_CLOSED"}

    @classmethod
    def poll(cls, context):
        return context.space_data.tree_type == "ScriptingNodesTree" and context.space_data.node_tree

    def draw(self, context):
        layout = self.layout
        
        layout.template_ID(context.scene.sn, "development_node", new="text.new", open="text.open")