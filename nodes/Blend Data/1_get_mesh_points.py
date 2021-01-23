import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_GetMeshPointsNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_GetMeshPointsNode"
    bl_label = "Get Mesh Points"
    # bl_icon = "GRAPH"
    bl_width_default = 160

    node_options = {
        "default_color": (0.3,0.3,0.3),
        "imperative_once": True
    }
    
    
    def on_create(self,context):
        inp = self.add_blend_data_input("Mesh/Object Data")
        inp.data_type = "Mesh"
        inp.data_identifier = "mesh"
        inp.data_name = "Mesh"
        out = self.add_blend_data_output("Vertices")
        out.subtype = "COLLECTION"
        out.data_type = "MeshVertices"
        out.data_name = "Vertices"
        out.data_identifier = "vertices"
        out = self.add_blend_data_output("Edges")
        out.subtype = "COLLECTION"
        out.data_type = "MeshEdges"
        out.data_name = "Edges"
        out.data_identifier = "edges"
        out = self.add_blend_data_output("Polygons")
        out.subtype = "COLLECTION"
        out.data_type = "MeshPolygons"
        out.data_name = "Polygons"
        out.data_identifier = "polygons"
    
    

    def code_evaluate(self, context, touched_socket):
        
        return {
            "code": f"{self.inputs[0].code()}.{touched_socket.data_identifier}"
        }