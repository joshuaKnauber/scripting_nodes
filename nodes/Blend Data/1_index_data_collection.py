import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode



class SN_IndexDataCollectionNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_IndexDataCollectionNode"
    bl_label = "Index Data Collection"
    # bl_icon = "GRAPH"
    bl_width_default = 160
    
    node_options = {
        "default_color": (0.3,0.3,0.3),
    }
    
    
    collection_error: bpy.props.BoolProperty(default=False)
        
    
    def update_return(self,context):
        if self.return_type == "INDEX" and (not len(self.inputs) or self.inputs[1].socket_type != "INTEGER"):
            self.inputs.remove(self.inputs[1])
            self.add_integer_input("Index").set_default(0)
            self.outputs[0].default_text = "Indexed Data Block"
        elif self.return_type == "NAME" and (not len(self.inputs) or self.inputs[0].socket_type != "STRING"):
            self.inputs.remove(self.inputs[1])
            self.add_string_input("Name")
            self.outputs[0].default_text = "Named Data Block"
        for link in self.outputs[0].links:
            link.to_socket.node.on_link_insert(link)


    return_type: bpy.props.EnumProperty(items=[("INDEX","Index","Object by name"),
                                               ("NAME","Name","Object by name")],
                                        name="Return Type",
                                        description="The type of returned object",
                                        update=update_return)
    
    
    def on_link_insert(self,link):
        if link.to_socket == self.inputs[0]:
            self.collection_error = False
            if link.from_socket.subtype == "COLLECTION":
                self.outputs[0].data_type = link.from_socket.data_type
                self.outputs[0].data_identifier = link.from_socket.data_identifier
                self.outputs[0].data_name = link.from_socket.data_name
                for link in self.outputs[0].links:
                    link.to_socket.node.on_link_insert(link)
            else:
                self.collection_error = True


    def on_create(self,context):
        inp = self.add_blend_data_input("Blend Data")
        inp.mirror_name = True
        inp.subtype = "COLLECTION"
        self.add_blend_data_output("Indexed Data Block")
        self.add_integer_input("Index").set_default(0)
        
        
    def draw_node(self,context,layout):
        if self.collection_error:
            layout.label(text="Connect data collection",icon="ERROR")
        layout.prop(self,"return_type",expand=True)


    def code_evaluate(self, context, touched_socket):

        if self.inputs[0].links:
            return {
                "code": f"{self.inputs[0].code()}[{self.inputs[1].code()}]"
            }
        else:
            self.add_error("No blend data", "Blend data input is not connected", True)
            return {"code": "None"}