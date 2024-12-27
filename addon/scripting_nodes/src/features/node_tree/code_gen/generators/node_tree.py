def code_gen_node_tree(ntree):
    return """
import bpy

class SNA_PT_AddonPanell(bpy.types.Panel):
    bl_idname = "SNA_PT_AddonPanell"
    bl_label = "WORKING"
    bl_space_type = 'PROPERTIES'
    bl_region_type = 'WINDOW'
    bl_context = "object"

    def draw(self, context: bpy.types.Context):
        self.layout.label(text="testing")
"""
