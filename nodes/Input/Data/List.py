import bpy
from ...base_node import SN_ScriptingBaseNode



class SN_ListNode(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_ListNode"
    bl_label = "List"
    node_color = "LIST"

    def on_create(self, context):
        self.add_dynamic_data_input("Data")
        self.add_list_output("List")

    def evaluate(self, context):
        items = [inp.python_value if inp.is_linked else None for inp in self.inputs[:-1]]
        items = filter(lambda item: item != None, items)
        self.outputs["List"].python_value = f"[{', '.join(items)}]"