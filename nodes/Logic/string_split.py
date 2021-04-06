import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_SplitStringNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_SplitStringNode"
    bl_label = "Split String"
    # bl_icon = "GRAPH"
    bl_width_default = 160


    node_options = {
        "default_color": (0.3,0.3,0.3),
    }


    def on_create(self,context):
        self.add_string_input("String")
        self.add_string_input("Split On")
        self.add_list_output("Split List")

    def code_evaluate(self, context, touched_socket):

        return {
            "code": f"""{self.inputs[0].code()}.split({self.inputs[1].code()})"""
        }