import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_BMeshToMeshNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_BMeshToMeshNode"
    bl_label = "Write BMesh To Mesh"

    def on_create(self, context):
        self.add_execute_input()
        self.add_property_input("BMesh")
        self.add_property_input("Mesh")
        self.add_execute_output()

    def evaluate(self, context):
        self.code_import = "import bmesh"
        self.code = f"""
            if {self.inputs["BMesh"].python_value} and {self.inputs["Mesh"].python_value}:
                {self.inputs["BMesh"].python_value}.to_mesh({self.inputs["Mesh"].python_value})
            {self.indent(self.outputs[0].python_value, 3)}
        """