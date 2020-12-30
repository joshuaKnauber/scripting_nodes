import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode



class SN_ObjectsNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_ObjectsNode"
    bl_label = "Objects"
    # bl_icon = "GRAPH"
    bl_width_default = 160
    
    node_options = {
        "default_color": (0.3,0.3,0.3),
    }
    
    
    def update_return(self,context):
        if self.return_type == "ALL" and len(self.inputs):
            self.inputs.clear()
            self.outputs[0].name = "All Objects"
        elif self.return_type == "INDEX" and (not len(self.inputs) or self.inputs[0].sn_type != "NUMBER"):
            self.inputs.clear()
            self.add_integer_input("Index")
            self.outputs[0].name = "Indexed Object"
        elif self.return_type == "NAME" and (not len(self.inputs) or self.inputs[0].sn_type != "STRING"):
            self.inputs.clear()
            self.add_string_input("Name")
            self.outputs[0].name = "Named Object"
    
    
    return_type: bpy.props.EnumProperty(items=[("ALL","All","All Objects"),
                                               ("INDEX","Index","Object by name"),
                                               ("NAME","Name","Object by name")],
                                        name="Return Type",
                                        description="The type of returned object",
                                        update=update_return)
    

    def on_create(self,context):
        self.add_blend_data_output("All Objects")
        
        
    def draw_node(self,context,layout):
        layout.prop(self,"return_type",expand=True)


    def code_evaluate(self, context, touched_socket):

        return {
            "code": f"""

                    """
        }