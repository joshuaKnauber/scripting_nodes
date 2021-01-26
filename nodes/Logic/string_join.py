import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_JoinListNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_JoinListNode"
    bl_label = "Join String List"
    # bl_icon = "GRAPH"
    bl_width_default = 160


    node_options = {
        "default_color": (0.3,0.3,0.3),
    }


    def on_create(self,context):
        self.add_list_input("List")
        self.add_string_input("Join On")
        self.add_string_output("String")


    def code_evaluate(self, context, touched_socket):

        if self.inputs[0].links:
            return {
                "code": f"""{self.inputs[1].code()}.join({self.inputs[0].code()})"""
            }
        else:
            self.add_error("No List", "You have to put in the list you want to use", True)
            return {
                "code": f"""{self.inputs[1].code()}.join({self.inputs[0].code()})"""
            }