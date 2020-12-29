import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode



class SN_SplitNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_SplitNode"
    bl_label = "Split"
    # bl_icon = "GRAPH"
    bl_width_default = 160
    
    node_options = {
        "default_color": (0.3,0.3,0.3),
    }


    def on_create(self,context):
        self.add_interface_input("Interface").copy_name = True
        self.add_interface_output("First Part")
        self.add_interface_output("Second Part")

        self.add_float_input("Factor").use_factor = True
        self.add_boolean_input("Align").set_default(False)
        self.add_boolean_input("Enabled")
        self.add_boolean_input("Alert").set_default(False)
        self.add_float_input("Scale X").set_default(1)
        self.add_float_input("Scale Y").set_default(1)

        
    def what_layout(self, socket):
        return "split"
    

    def code_evaluate(self, context, touched_socket):

        layout = touched_socket.links[0].from_node.what_layout(touched_socket.links[0].from_socket)
        
        return {
            "code": f"""

                    split = {layout}.split(align={self.inputs["Align"].value},factor={self.inputs["Factor"].value})
                    split.enabled = {self.inputs["Enabled"].value}
                    split.alert = {self.inputs["Alert"].value}
                    split.scale_x = {self.inputs["Scale X"].value}
                    split.scale_y = {self.inputs["Scale Y"].value}
                    {self.outputs[0].block(5)}
                    {self.outputs[1].block(5)}
                    """
        }