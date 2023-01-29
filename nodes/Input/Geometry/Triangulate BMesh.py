import bpy
from ...base_node import SN_ScriptingBaseNode



class SN_TriangulateBmeshNode(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_TriangulateBmeshNode"
    bl_label = "Triangulate BMesh"
    node_color = "PROGRAM"

    def on_create(self, context):
        self.add_execute_input()
        self.add_property_input("BMesh")
        self.add_execute_output()
        self.add_property_output("BMesh")

    def evaluate(self, context):
        self.code = f"""
            bm_{self.static_uid} = {self.inputs["BMesh"].python_value}.copy()
            bmesh.ops.triangulate(bm_{self.static_uid}, faces=bm_{self.static_uid}.faces)
            bm_{self.static_uid}.verts.ensure_lookup_table()
            bm_{self.static_uid}.faces.ensure_lookup_table()
            bm_{self.static_uid}.edges.ensure_lookup_table()
            {self.indent(self.outputs[0].python_value, 3)}
        """

        self.outputs["BMesh"].python_value = f"bm_{self.static_uid}"