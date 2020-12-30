import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode



class SN_FindNameInCollectionNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_FindNameInCollectionNode"
    bl_label = "Find Name In Data Collection"
    # bl_icon = "GRAPH"
    bl_width_default = 160
    
    node_options = {
        "default_color": (0.3,0.3,0.3),
    }
    
    
    collection_error: bpy.props.BoolProperty(default=False)
    
        
    
    def update_return(self,context):
        if self.return_type == "INDEX" and (not len(self.inputs) or self.inputs[1].sn_type != "NUMBER"):
            self.inputs.remove(self.inputs[1])
            self.add_integer_input("Index")
            self.outputs[0].name = "Indexed Data Block"
        elif self.return_type == "NAME" and (not len(self.inputs) or self.inputs[0].sn_type != "STRING"):
            self.inputs.remove(self.inputs[1])
            self.add_string_input("Name")
            self.outputs[0].name = "Named Data Block"
        if self.outputs[0].is_linked:
            self.outputs[0].links[0].to_node.on_link_insert(self.outputs[0].links[0])
    
    
    return_type: bpy.props.EnumProperty(items=[("INDEX","Index","Object by name"),
                                               ("NAME","Name","Object by name")],
                                        name="Return Type",
                                        description="The type of returned object",
                                        update=update_return)
    
    
    def on_link_insert(self,link):
        self.collection_error = False
        if link.to_socket == self.inputs[0]:
            if link.from_socket.collection:
                self.outputs[0].data_type = link.from_socket.data_type
            else:
                self.collection_error = True


    def on_create(self,context):
        self.add_blend_data_input("Blend Data").copy_name = True
        out = self.add_blend_data_output("Indexed Data Block")
        self.add_integer_input("Index")
        
        
    def draw_node(self,context,layout):
        if self.collection_error:
            layout.label(text="Connect data collection",icon="ERROR")
        layout.prop(self,"return_type",expand=True)


    def code_evaluate(self, context, touched_socket):

        return {
            "code": f"""

                    """
        }
        
#TODO function for node to choose one value based on bool | like if but inline with function