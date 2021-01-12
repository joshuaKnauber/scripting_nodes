import bpy



class SN_SceneDataBase():

    # bl_icon = "GRAPH"
    bl_width_default = 160
    
    active_data = ""
    
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
            self.outputs[0].subtype = "DATA_BLOCK"
        elif self.return_type == "NAME" and (not len(self.inputs) or self.inputs[0].socket_type != "STRING"):
            self.inputs.clear()
            self.add_string_input("Name")
            self.outputs[0].default_text = "Named"
            self.outputs[0].subtype = "DATA_BLOCK"
        if self.outputs[0].is_linked:
            self.outputs[0].links[0].to_node.on_link_insert(self.outputs[0].links[0])
    
    
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
        
        if self.active_data:
            out = self.add_blend_data_output("Active")
            out.subtype = "DATA_BLOCK"
            out.data_type = self.data_type
            out.data_identifier = self.active_data.split(".")[-1]
        
        
    def draw_node(self,context,layout):
        layout.prop(self,"return_type",expand=True)


    def code_evaluate(self, context, touched_socket):

        if touched_socket == self.outputs[0]:
            limiter = ""
            if self.return_type != "ALL":
                limiter = f"[{self.inputs[0].code()}]"

            return {
                "code": f"bpy.data.{self.outputs[0].data_identifier}{limiter}"
            }
            
        else:
            return {
                "code": f"{self.active_data}"
            }