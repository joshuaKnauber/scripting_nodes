import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode



class SN_ColumnNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_ColumnNode"
    bl_label = "Column"
    # bl_icon = "GRAPH"
    bl_width_default = 160
    
    node_options = {
        "default_color": (0.3,0.3,0.3),
    }


    def on_create(self,context):
        self.add_interface_input("Interface").mirror_name = True
        self.add_interface_output("Column")
        self.add_dynamic_interface_output("Column")

        self.add_boolean_input("Align").set_default(False)
        self.add_boolean_input("Enabled")
        self.add_boolean_input("Alert").set_default(False)
        self.add_float_input("Scale X").set_default(1)
        self.add_float_input("Scale Y").set_default(1)

        
    def what_layout(self, socket):
        return "col"
    

    def code_evaluate(self, context, touched_socket):

        layout = touched_socket.links[0].from_node.what_layout(touched_socket.links[0].from_socket)


        return {
            "code": f"""

                    col = {layout}.column(align={self.inputs["Align"].code()})
                    col.enabled = {self.inputs["Enabled"].code()}
                    col.alert = {self.inputs["Alert"].code()}
                    col.scale_x = {self.inputs["Scale X"].code()}
                    col.scale_y = {self.inputs["Scale Y"].code()}
                    {self.outputs[0].by_name(5)}
                    """
        }