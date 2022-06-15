import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_CreateEmptyBmeshNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_CreateEmptyBmeshNode"
    bl_label = "Create Empty BMesh"

    def on_create(self, context):
        self.add_execute_input()
        self.add_execute_output()
        self.add_property_output("BMesh")
        
    def draw_node(self, context, layout):
        layout.label(text="Free the BMesh when you are done editing!", icon="ERROR")

    def evaluate(self, context):
        self.code_import = "import bmesh"
        self.code = f"""
            bm_{self.static_uid} = bmesh.new()
            {self.indent(self.outputs[0].python_value, 3)}
        """
        self.outputs["BMesh"].python_value = f"bm_{self.static_uid}"