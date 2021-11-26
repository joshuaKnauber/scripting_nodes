import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode



class SN_JoinStringsNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_JoinStringsNode"
    bl_label = "Join Strings"

    def on_create(self, context):
        self.add_string_input("Delimiter")
        self.add_string_input("String")
        self.add_string_input("String")
        self.add_string_output("String")

    def evaluate(self, context):
        values = [inp.python_value for inp in self.inputs[1:]]
        join_op = f"+{self.inputs['Delimiter'].python_value}+".join(values)
        self.outputs["String"].python_value = join_op