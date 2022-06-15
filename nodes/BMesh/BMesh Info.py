import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_BMeshInfoNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_BMeshInfoNode"
    bl_label = "BMesh Info"

    def on_create(self, context):
        self.add_property_input("BMesh")
        self.add_boolean_output("Has Been Freed")
        self.add_boolean_output("Belongs To Mesh")
        self.add_enum_set_output("Select Mode")

    def evaluate(self, context):
        self.code_import = "import bmesh"
        self.outputs['Has Been Freed'].python_value = f"(not {self.inputs[0].python_value}.is_valid)"
        self.outputs['Belongs To Mesh'].python_value = f"{self.inputs[0].python_value}.is_wrapped"
        self.outputs['Select Mode'].python_value = f"{self.inputs[0].python_value}.select_mode"
