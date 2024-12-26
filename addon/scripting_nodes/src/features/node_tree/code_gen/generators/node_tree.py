def code_gen_node_tree(ntree):
    return """
import bpy

class SNA_PT_AddonPanell(bpy.types.Panel):
    bl_idname = "SNA_PT_AddonPanell"
    bl_label = "WORKING"
    bl_space_type = "NODE_EDITOR"
    bl_region_type = "UI"
    bl_category = "Scripting Nodes"

    def draw(self, context: bpy.types.Context):
        pass
"""
