import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_InverseBooleanNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_InverseBooleanNode"
    bl_label = "Inverse Boolean"
    # bl_icon = "GRAPH"
    bl_width_default = 160

    node_options = {
        "default_color": (0.3,0.3,0.3),
    }


    def on_create(self,context):
        self.add_boolean_input("Boolean")
        self.add_boolean_output("Inversed Boolean")


    def code_evaluate(self, context, touched_socket):

        return {
            "code": f"""not {self.inputs[0].value}"""
        }