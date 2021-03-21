import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_IsInStringNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_IsInStringNode"
    bl_label = "Substring is in String"
    # bl_icon = "GRAPH"
    bl_width_default = 160

    node_options = {
        "default_color": (0.3,0.3,0.3),
    }

    def on_create(self,context):
        self.add_string_input("Subtring")
        self.add_string_input("String")
        self.add_boolean_output("Is in String")


    def code_evaluate(self, context, touched_socket):
        
        return {
            "code": f"{self.inputs[0].code()} in {self.inputs[1].code()}"
        }