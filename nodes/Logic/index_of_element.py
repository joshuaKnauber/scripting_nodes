import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_IndexElementNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_IndexElementNode"
    bl_label = "Index of Element in List"
    # bl_icon = "GRAPH"
    bl_width_default = 160


    node_options = {
        "default_color": (0.3,0.3,0.3),
    }


    def on_create(self,context):
        self.add_list_input("List")
        self.add_data_input("Element")
        self.add_integer_output("Index of Element")


    def code_evaluate(self, context, touched_socket):

        return {
            "code": f"""{self.inputs[0].code()}.index({self.inputs[1].code()})"""
        }