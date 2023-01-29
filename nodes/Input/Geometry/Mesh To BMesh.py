import bpy
from ...base_node import SN_ScriptingBaseNode



class SN_ObjectToBMeshNode(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_ObjectToBMeshNode"
    bl_label = "Object To BMesh"
    node_color = "PROGRAM"

    def on_create(self, context):
        self.add_execute_input()
        self.add_property_input("Object")
        self.add_boolean_input("Use Edit Mode").default_value = True
        self.add_boolean_input("Use Evaluated Mesh")
        self.add_boolean_input("Use Object Transforms").default_value = True
        self.add_execute_output()
        self.add_property_output("BMesh")
        
    def evaluate(self, context):
        self.code_import = f"import bmesh"

        self.code = f"""
            bm_{self.static_uid} = bmesh.new()
            if {self.inputs["Object"].python_value}:
                if {self.inputs["Object"].python_value}.mode == 'EDIT' and {self.inputs["Use Edit Mode"].python_value}:
                    bm_{self.static_uid} = bmesh.from_edit_mesh({self.inputs["Object"].python_value}.data)
                else:
                    if {self.inputs["Use Evaluated Mesh"].python_value}:
                        dg = bpy.context.evaluated_depsgraph_get()
                        bm_{self.static_uid}.from_mesh({self.inputs["Object"].python_value}.evaluated_get(dg).to_mesh())
                    else:
                        bm_{self.static_uid}.from_mesh({self.inputs["Object"].python_value}.data)
            if {self.inputs["Use Object Transforms"].python_value}:
                bm_{self.static_uid}.transform({self.inputs["Object"].python_value}.matrix_world)
            bm_{self.static_uid}.verts.ensure_lookup_table()
            bm_{self.static_uid}.faces.ensure_lookup_table()
            bm_{self.static_uid}.edges.ensure_lookup_table()
            {self.indent(self.outputs[0].python_value, 3)}
        """

        self.outputs["BMesh"].python_value = f"bm_{self.static_uid}"