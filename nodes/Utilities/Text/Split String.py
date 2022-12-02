import bpy
from ...base_node import SN_ScriptingBaseNode



class SN_SplitStringNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_SplitStringNode"
    bl_label = "Split String"
    node_color = "STRING"
    bl_width_default = 200

    def on_create(self, context):
        self.add_string_input("String")
        self.add_string_input("Split On")
        self.add_list_output("Split List")

    def evaluate(self, context):
        self.outputs["Split List"].python_value = f"{self.inputs['String'].python_value}.split({self.inputs['Split On'].python_value})"