import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_GetElementListNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_GetElementListNode"
    bl_label = "Get Element of List"
    # bl_icon = "GRAPH"
    bl_width_default = 160


    node_options = {
        "default_color": (0.3,0.3,0.3),
    }


    def on_create(self,context):
        self.add_list_input("List")
        self.add_integer_input("Index of Element").set_default(0)
        self.add_data_output("Element")


    def code_evaluate(self, context, touched_socket):

        return {
            "code": f"""{self.inputs[0].code()}[{self.inputs[1].code()}]"""
        }