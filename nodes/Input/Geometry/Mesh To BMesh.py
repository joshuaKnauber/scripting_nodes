import bpy
from ...base_node import SN_ScriptingBaseNode



class SN_ObjectToBMeshNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_ObjectToBMeshNode"
    bl_label = "Object To BMesh"
    node_color = "PROGRAM"

    def on_create(self, context):
        self.add_execute_input()
        self.add_property_input("Object")
        self.add_execute_output()
        self.add_property_output("BMesh")
        
    def evaluate(self, context):
        self.code_import = f"import bmesh"

        self.code = f"""
            bm_{self.static_uid} = bmesh.new()
            if {self.inputs["Object"].python_value}:
                if {self.inputs["Object"].python_value}.mode == 'EDIT':
                    bm_{self.static_uid} = bmesh.from_edit_mesh({self.inputs["Object"].python_value}.data)
                else:
                    bm_{self.static_uid}.from_mesh({self.inputs["Object"].python_value}.data)
            bm_{self.static_uid}.verts.ensure_lookup_table()
            bm_{self.static_uid}.faces.ensure_lookup_table()
            {self.indent(self.outputs[0].python_value, 3)}
        """

        self.outputs["BMesh"].python_value = f"bm_{self.static_uid}"