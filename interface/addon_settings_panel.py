import bpy

class SN_PT_AddonSettingsPanel(bpy.types.Panel):
    """Creates a panel that lets you edit the Addon Settings for the current NodeTree"""
    bl_label = "Settings"
    bl_order = 2
    bl_idname = "SN_PT_AddonSettingsPanel"
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'UI'
    bl_category = "Visual Scripting"

    @classmethod
    def poll(cls, context):
        if context.space_data.tree_type == 'ScriptingNodesTree':
            return context.space_data.node_tree != None

    def draw(self, context):
        layout = self.layout
        layout.prop(context.space_data.node_tree,"compile_on_start")