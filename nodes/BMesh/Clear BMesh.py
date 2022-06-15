import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_ClearBMeshNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_ClearBMeshNode"
    bl_label = "Clear BMesh"

    def on_create(self, context):
        self.add_execute_input()
        self.add_property_input("BMesh")
        self.add_execute_output()

    def evaluate(self, context):
        self.code_import = "import bmesh"
        self.code = f"""
            if {self.inputs["BMesh"].python_value}:
                {self.inputs["BMesh"].python_value}.clear()
            {self.indent(self.outputs[0].python_value, 3)}
        """