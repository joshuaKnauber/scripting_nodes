import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_BMeshDataNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_BMeshDataNode"
    bl_label = "BMesh Data"

    def on_create(self, context):
        self.add_property_input("BMesh")
        self.add_collection_property_output("Vertices")
        self.add_collection_property_output("Edges")
        self.add_collection_property_output("Faces")
        self.add_collection_property_output("Loops")

    def evaluate(self, context):
        self.code_import = "import bmesh"

        self.code_imperative = """
            def get_bmesh_data(bm, attr):
                data = getattr(bm, attr)
                data.ensure_lookup_table()
                return data
        """
        
        self.outputs['Vertices'].python_value = f"get_bmesh_data({self.inputs[0].python_value}, 'verts')"
        self.outputs['Edges'].python_value = f"get_bmesh_data({self.inputs[0].python_value}, 'edges')"
        self.outputs['Faces'].python_value = f"get_bmesh_data({self.inputs[0].python_value}, 'faces')"
        self.outputs['Loops'].python_value = f"get_bmesh_data({self.inputs[0].python_value}, 'loops')"
