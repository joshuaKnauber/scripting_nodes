import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_ReplaceStringNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_ReplaceStringNode"
    bl_label = "Replace In String"
    # bl_icon = "GRAPH"
    bl_width_default = 160


    node_options = {
        "default_color": (0.3,0.3,0.3),
    }


    def on_create(self,context):
        self.add_string_input("String")
        self.add_string_input("Old")
        self.add_string_input("New")
        self.add_string_output("String")


    def code_evaluate(self, context, touched_socket):

        return {
            "code": f"""{self.inputs[0].code()}.replace({self.inputs[1].code()}, {self.inputs[2].code()})"""
        }