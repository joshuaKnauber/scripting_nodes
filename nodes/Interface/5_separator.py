import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode



class SN_SeparatorNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_SeparatorNode"
    bl_label = "Separator"
    # bl_icon = "GRAPH"
    bl_width_default = 160
    
    node_options = {
        "default_color": (0.3,0.3,0.3),
    }


    def on_create(self,context):
        self.add_interface_input("Interface").mirror_name = True
        self.add_float_input("Factor")


    def code_evaluate(self, context, touched_socket):

        return {
            "code": f"""
                    {touched_socket.links[0].from_node.what_layout(touched_socket.links[0].from_socket)}.separator(factor={self.inputs[1].code()})
                    """
        }