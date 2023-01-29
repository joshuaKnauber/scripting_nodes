import bpy
from ...base_node import SN_ScriptingBaseNode



class SN_NgonToTriangleLocationsNode(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_NgonToTriangleLocationsNode"
    bl_label = "Ngon To Triangle Locations"
    node_color = "PROPERTY"

    def on_create(self, context):
        self.add_property_input("Ngon")
        self.add_list_output("Triangle Locations")

    def evaluate(self, context):
        self.code_imperative = """
        def ngon_to_triangle_locations(ngon):
            bm = bmesh.new()
            for v in ngon.verts:
                bm.verts.new(v.co)
            bm.faces.new(bm.verts)
            bmesh.ops.triangulate(bm, faces=bm.faces)
            bm.verts.ensure_lookup_table()
            new_faces = []
            for f in bm.faces:
                vert_locations = []
                for v in f.verts:
                    vert_locations.append(tuple(v.co))
                new_faces.append(vert_locations)
            return new_faces
        """

        self.outputs["Triangle Locations"].python_value = f"ngon_to_triangle_locations({self.inputs['Ngon'].python_value})"