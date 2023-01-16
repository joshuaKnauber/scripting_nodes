import bpy
from ...base_node import SN_ScriptingBaseNode



class SN_BlenderDataNode(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_BlenderDataNode"
    bl_label = "Blender Data"
    node_color = "PROPERTY"

    def on_create(self, context):
        self.add_property_output("Current Context")
        self.add_property_output("Blend Data")
        self.add_property_output("App")
        self.add_property_output("Path")
        
    def evaluate(self, context):
        self.outputs["Current Context"].python_value = "bpy.context"
        self.outputs["Blend Data"].python_value = "bpy.data"
        self.outputs["App"].python_value = "bpy.app"
        self.outputs["Path"].python_value = "bpy.path"