import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode



class SN_RowNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_RowNode"
    bl_label = "Row"
    # bl_icon = "GRAPH"
    bl_width_default = 160
    
    node_options = {
        "default_color": (0.3,0.3,0.3),
    }


    def on_create(self,context):
        self.add_interface_input("Interface").copy_name = True
        self.add_interface_output("Row",True)
        self.add_dynamic_interface_output("Row")

        self.add_boolean_input("Align").default(False)
        self.add_boolean_input("Enabled")
        self.add_boolean_input("Alert").default(False)
        self.add_float_input("Scale X")
        self.add_float_input("Scale Y")

        
    def what_layout(self, socket):
        return "row"
    

    def code_evaluate(self, context, main_tree, touched_socket):

        layout = touched_socket.links[0].from_node.what_layout(touched_socket.links[0].from_socket)
        
        row_layouts = []
        for out in self.outputs:
            if out.name == "Row":
                row_layouts.append(out.block(0))

        return {
            "code": f"""

                    row = {layout}.row(align={self.inputs["Align"].value})
                    row.enabled = {self.inputs["Enabled"].value}
                    row.alert = {self.inputs["Alert"].value}
                    row.scale_x = {self.inputs["Scale X"].value}
                    row.scale_y = {self.inputs["Scale Y"].value}
                    {self.list_blocks(row_layouts, 5)}
                    
                    """
        }