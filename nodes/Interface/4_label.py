import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode



class SN_LabelNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_LabelNode"
    bl_label = "Label"
    # bl_icon = "GRAPH"
    bl_width_default = 160
    
    node_options = {
        "default_color": (0.3,0.3,0.3),
    }


    def on_create(self,context):
        self.add_interface_input("Interface").copy_name = True

        self.add_string_input("Text")
        self.add_icon_input("Icon")
    

    def code_evaluate(self, context, touched_socket):

        layout = touched_socket.links[0].from_node.what_layout(touched_socket.links[0].from_socket)

        icon = self.inputs['Icon'].icon_line()
        
        return {
            "code": f"""
                    {layout}.label(text={self.inputs['Text'].value},{icon})
                    """
        }