import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_SortListNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_SortListNode"
    bl_label = "Sort List"
    node_color = "LIST"

    def on_create(self, context):
        self.add_list_input()
        self.add_boolean_input("Reverse").default_value = False
        self.add_list_output()

    def evaluate(self, context):
        self.outputs[0].python_value = f"sorted({self.inputs[0].python_value}, reverse={self.inputs['Reverse'].python_value})"