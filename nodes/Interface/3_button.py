import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode



class SN_ButtonNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_ButtonNode"
    bl_label = "Button"
    # bl_icon = "GRAPH"
    bl_width_default = 160
    
    node_options = {
        "default_color": (0.3,0.3,0.3),
    }


    def on_create(self,context):
        self.add_interface_input("Interface").copy_name = True

        self.add_string_input("Label").set_default("New Button")
        self.add_boolean_input("Emboss").set_default(True)
        self.add_boolean_input("Depress").set_default(False)
        self.add_icon_input("Icon")
    

    def code_evaluate(self, context, touched_socket):

        layout = touched_socket.links[0].from_node.what_layout(touched_socket.links[0].from_socket)
        text = self.inputs['Label'].value
        emboss = self.inputs['Emboss'].value
        depress = self.inputs['Depress'].value
        icon = self.inputs['Icon'].icon_line()
        
        operator = "object.add"
        
        return {
            "code": f"""
                    op = {layout}.operator("{operator}",text={text},emboss={emboss},depress={depress},{icon})
                    """
        }