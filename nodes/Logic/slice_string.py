import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_SliceStringNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_SliceStringNode"
    bl_label = "Slice String"
    # bl_icon = "GRAPH"
    bl_width_default = 160


    node_options = {
        "default_color": (0.3,0.3,0.3),
    }


    def on_create(self,context):
        self.add_string_input("String")
        self.add_integer_input("Index").set_default(0)
        self.add_string_output("Before")
        self.add_string_output("After")


    def code_evaluate(self, context, touched_socket):
        
        before, after = "", ""
        if touched_socket == self.outputs[0]:
            before = ":"
        else:
            after = ":"

        return {
            "code": f"""{self.inputs[0].code()}[{before}{self.inputs[1].code()}{after}]"""
        }