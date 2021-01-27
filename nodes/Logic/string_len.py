import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_StringLenNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_StringLenNode"
    bl_label = "String Length"
    # bl_icon = "GRAPH"
    bl_width_default = 160


    node_options = {
        "default_color": (0.3,0.3,0.3),
    }


    def on_create(self,context):
        self.add_string_input("String")
        self.add_integer_output("Length")


    def code_evaluate(self, context, touched_socket):

        return {
            "code": f"""len({self.inputs[0].code()})"""
        }