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
        self.add_interface_input("Interface").copy_name = True
        self.add_interface_output("Column",True)
        self.add_dynamic_interface_output("Column")

        self.add_boolean_input("Align").set_default(False)
        self.add_boolean_input("Enabled")
        self.add_boolean_input("Alert").set_default(False)
        self.add_float_input("Scale X")
        self.add_float_input("Scale Y")

        
    def what_layout(self, socket):
        return "col"
    

    def code_evaluate(self, context, touched_socket):

        layout = touched_socket.links[0].from_node.what_layout(touched_socket.links[0].from_socket)
        
        column_layouts = []
        for out in self.outputs:
            if out.name == "Column":
                column_layouts.append(out.block(0))

        return {
            "code": f"""

                    col = {layout}.column(align={self.inputs["Align"].value})
                    col.enabled = {self.inputs["Enabled"].value}
                    col.alert = {self.inputs["Alert"].value}
                    col.scale_x = {self.inputs["Scale X"].value}
                    col.scale_y = {self.inputs["Scale Y"].value}
                    {self.list_blocks(column_layouts, 5)}
                    """
        }