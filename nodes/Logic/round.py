import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_RoundNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_RoundNode"
    bl_label = "Round"
    # bl_icon = "GRAPH"
    bl_width_default = 160

    node_options = {
        "default_color": (0.3,0.3,0.3),
    }

    def on_create(self,context):
        self.add_float_input("Value")
        self.add_integer_input("Decimals")
        self.add_float_output("Rounded Number")


    def code_evaluate(self, context, touched_socket):

        return {
            "code": f"""round({self.inputs[0].value}, abs({self.inputs[1].value}))"""
        }