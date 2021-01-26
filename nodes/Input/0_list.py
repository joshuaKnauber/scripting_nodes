import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_ListNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_ListNode"
    bl_label = "List"
    # bl_icon = "GRAPH"
    bl_width_default = 160

    node_options = {
        "default_color": (0.3,0.3,0.3),
    }


    def on_create(self,context):
        self.add_list_output("List").mirror_name = True
        self.add_dynamic_data_input("Value")


    def code_evaluate(self, context, touched_socket):
        value_list = ""
        for inp in self.inputs[:-1]:
            value_list+=inp.code() + ", "

        return {
            "code": f"[{value_list}]"
        }