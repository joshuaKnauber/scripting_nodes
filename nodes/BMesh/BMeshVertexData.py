import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_BMeshVertexDataNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_BMeshVertexDataNode"
    bl_label = "BMesh Vertex Data"

    def on_create(self, context):
        self.add_property_input("BMesh Vertex")
        
        self.add_property_output("Location")
        self.add_float_vector_output("Location")
        self.add_property_output("Hidden")
        self.add_boolean_output("Hidden")
        self.add_property_output("Selected")
        self.add_boolean_output("Selected")
        self.add_integer_output("Index")
        self.add_float_vector_output("Normal")

    def evaluate(self, context):
        self.code_import = "import bmesh"
        
        self.outputs[0].python_value = f"{self.inputs[0].python_value}.co"
        self.outputs[1].python_value = f"{self.inputs[0].python_value}.co"
        self.outputs[2].python_value = f"{self.inputs[0].python_value}.hide"
        self.outputs[3].python_value = f"{self.inputs[0].python_value}.hide"
        self.outputs[4].python_value = f"{self.inputs[0].python_value}.select"
        self.outputs[5].python_value = f"{self.inputs[0].python_value}.select"
        self.outputs[6].python_value = f"{self.inputs[0].python_value}.index"
        self.outputs[7].python_value = f"{self.inputs[0].python_value}.normal"