import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_BlenderDataNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_BlenderDataNode"
    bl_label = "Blender Data"
    node_color = "BLEND_DATA"

    def on_create(self, context):
        self.add_blend_data_output("Current Context")
        self.add_blend_data_output("Blend Data")
        self.add_blend_data_output("App")
        self.add_blend_data_output("Path")
        
    def evaluate(self, context):
        self.outputs["Current Context"].python_value = "bpy.context"
        self.outputs["Blend Data"].python_value = "bpy.data"
        self.outputs["App"].python_value = "bpy.app"
        self.outputs["Path"].python_value = "bpy.path"