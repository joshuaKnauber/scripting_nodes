import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_BMeshVertexInfoNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_BMeshVertexInfoNode"
    bl_label = "BMesh Vertex Info"

    def on_create(self, context):
        self.add_property_input("BMesh Vertex")
        
        self.add_collection_property_output("Linked Edges")
        self.add_collection_property_output("Linked Faces")
        self.add_collection_property_output("Linked Loops")
        self.add_boolean_output("Is Part Of Boundary Edge")
        self.add_boolean_output("Is Manifold")
        self.add_boolean_output("Has Not Been Removed")
        self.add_boolean_output("Is Not Connected To Face")

    def evaluate(self, context):
        self.code_import = "import bmesh"
        
        self.outputs[0].python_value = f"{self.inputs[0].python_value}.link_edges"
        self.outputs[1].python_value = f"{self.inputs[0].python_value}.link_faces"
        self.outputs[2].python_value = f"{self.inputs[0].python_value}.link_loops"
        self.outputs[3].python_value = f"{self.inputs[0].python_value}.is_boundary"
        self.outputs[4].python_value = f"{self.inputs[0].python_value}.is_manifold"
        self.outputs[5].python_value = f"{self.inputs[0].python_value}.is_valid"
        self.outputs[6].python_value = f"{self.inputs[0].python_value}.is_wire"
