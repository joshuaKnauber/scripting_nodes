import bpy
from ...base_node import SN_ScriptingBaseNode



class SN_BMeshDataNode(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_BMeshDataNode"
    bl_label = "BMesh Object Data"
    node_color = "PROPERTY"

    def on_create(self, context):
        self.add_property_input("BMesh")
        self.add_collection_property_output("Vertices")
        self.add_collection_property_output("Faces")
        self.add_collection_property_output("Edges")
        
    def evaluate(self, context):
        if self.inputs["BMesh"].is_linked:
            self.outputs["Vertices"].python_value = f"{self.inputs['BMesh'].python_value}.verts"
            self.outputs["Faces"].python_value = f"{self.inputs['BMesh'].python_value}.faces"
            self.outputs["Edges"].python_value = f"{self.inputs['BMesh'].python_value}.edges"
        else:
            self.outputs["Vertices"].reset_value()
            self.outputs["Faces"].reset_value()
            self.outputs["Edges"].reset_value()