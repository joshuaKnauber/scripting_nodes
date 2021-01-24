import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_PathAbsoluteNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_PathAbsoluteNode"
    bl_label = "Make Path Absolute"
    # bl_icon = "GRAPH"
    bl_width_default = 160


    node_options = {
        "default_color": (0.3,0.3,0.3),
    }


    def on_create(self,context):
        self.add_string_input("Relative").subtype = "FILE"
        self.add_string_output("Absolute").subtype = "FILE"


    def code_evaluate(self, context, touched_socket):

        return {
            "code": f"""bpy.path.abspath({self.inputs[0].code()})"""
        }