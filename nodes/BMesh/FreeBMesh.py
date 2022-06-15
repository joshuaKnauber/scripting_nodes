import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_FreeBMeshNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_FreeBMeshNode"
    bl_label = "Free BMesh"

    def on_create(self, context):
        self.add_execute_input()
        self.add_property_input("BMesh")
        self.add_execute_output()

    def evaluate(self, context):
        self.code_import = "import bmesh"
        self.code = f"""
            if {self.inputs["BMesh"].python_value}:
                {self.inputs["BMesh"].python_value}.free()
            {self.indent(self.outputs[0].python_value, 3)}
        """