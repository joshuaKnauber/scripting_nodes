import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_JoinStringsNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_JoinStringsNode"
    bl_label = "Join Strings"
    node_color = "STRING"
    bl_width_default = 200

    def on_create(self, context):
        self.add_list_input("String List")
        self.add_string_input("Join On")
        self.add_string_output("String")

    def evaluate(self, context):
        self.outputs["String"].python_value = f"{self.inputs['Join On'].python_value}.join({self.inputs['String List'].python_value})"