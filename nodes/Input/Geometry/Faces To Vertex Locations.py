import bpy
from ...base_node import SN_ScriptingBaseNode



class SN_FacesToVertexLocationsNode(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_FacesToVertexLocationsNode"
    bl_label = "BMesh Faces To Vertex Locations"
    node_color = "PROPERTY"

    def on_create(self, context):
        self.add_collection_property_input("Faces")
        self.add_list_output("All Locations")
        self.add_list_output("Quad Locations Only")
        self.add_list_output("Triangle Locations Only")
        self.add_list_output("Ngon Locations Only")
        
    def evaluate(self, context):
        self.code_imperative = f"""
            def get_bmesh_vertex_locations(faces):
                locations = []
                for face in faces:
                    face_locations = []
                    for vert in face.verts:
                        face_locations.append(vert.co)
                    locations.append(face_locations)
                return locations
            
            def get_bmesh_vertex_locations_quads(faces):
                locations = get_bmesh_vertex_locations(faces)
                return [loc for loc in locations if len(loc) == 4]

            def get_bmesh_vertex_locations_triangles(faces):
                locations = get_bmesh_vertex_locations(faces)
                return [loc for loc in locations if len(loc) == 3]
            
            def get_bmesh_vertex_locations_ngons(faces):
                locations = get_bmesh_vertex_locations(faces)
                return [loc for loc in locations if len(loc) > 4]
        """

        self.outputs["All Locations"].python_value = f"get_bmesh_vertex_locations({self.inputs['Faces'].python_value})"
        self.outputs["Quad Locations Only"].python_value = f"get_bmesh_vertex_locations_quads({self.inputs['Faces'].python_value})"
        self.outputs["Triangle Locations Only"].python_value = f"get_bmesh_vertex_locations_triangles({self.inputs['Faces'].python_value})"
        self.outputs["Ngon Locations Only"].python_value = f"get_bmesh_vertex_locations_ngons({self.inputs['Faces'].python_value})"