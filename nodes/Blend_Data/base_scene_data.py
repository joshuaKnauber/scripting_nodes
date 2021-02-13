import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode



class SN_SceneDataBase():

    # bl_icon = "GRAPH"
    bl_width_default = 160
    
    active_data = ""
    selected_data = ""
    
    node_options = {
        "default_color": (0.3,0.3,0.3),
    }
    
    def update_return(self,context):
        if self.return_type == "ALL" and len(self.inputs):
            self.inputs.clear()
            self.outputs[0].default_text = "All"
            self.outputs[0].subtype = "COLLECTION"
        elif self.return_type == "INDEX" and (not len(self.inputs) or self.inputs[0].socket_type != "INTEGER"):
            self.inputs.clear()
            self.add_integer_input("Index").set_default(0)
            self.outputs[0].default_text = "Indexed"
            self.outputs[0].subtype = "NONE"
        elif self.return_type == "NAME" and (not len(self.inputs) or self.inputs[0].socket_type != "STRING"):
            self.inputs.clear()
            self.add_string_input("Name")
            self.outputs[0].default_text = "Named"
            self.outputs[0].subtype = "NONE"
        for link in self.outputs[0].links:
            link.to_socket.node.on_link_insert(link)
    
    
    return_type: bpy.props.EnumProperty(items=[("ALL","All","All"),
                                               ("INDEX","Index","By index"),
                                               ("NAME","Name","By name")],
                                        name="Return Type",
                                        description="The type of returned blend data",
                                        update=update_return)
    

    def on_create(self,context):
        out = self.add_blend_data_output("All")
        out.subtype = "COLLECTION"
        out.data_type = self.data_type
        out.data_identifier = self.data_identifier
        out.data_name = self.data_type
        
        if self.active_data:
            out = self.add_blend_data_output("Active")
            out.subtype = "NONE"
            out.data_type = self.data_type
            out.data_identifier = self.active_data.split(".")[-1]
            out.data_name = self.data_type
        
        if self.selected_data:
            out = self.add_blend_data_output("Selected")
            out.subtype = "COLLECTION"
            out.data_type = self.data_type
            out.data_identifier = self.selected_data.split(".")[-1]
            out.data_name = self.data_type

        
    def draw_node(self,context,layout):
        layout.prop(self,"return_type",expand=True)


    def code_evaluate(self, context, touched_socket):

        if touched_socket == self.outputs[0]:
            limiter = ""
            if self.return_type != "ALL":
                limiter = f"[{self.inputs[0].code()}]"

            return {
                "code": f"bpy.data.{self.data_identifier}{limiter}"
            }
            
        elif touched_socket == self.outputs[1]:
            return {
                "code": f"{self.active_data}"
            }
        
        else:
            return {
                "code": f"{self.selected_data}"
            }