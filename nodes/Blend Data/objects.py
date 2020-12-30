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
            self.outputs[0].collection = True
        elif self.return_type == "INDEX" and (not len(self.inputs) or self.inputs[0].sn_type != "NUMBER"):
            self.inputs.clear()
            self.add_integer_input("Index")
            self.outputs[0].name = "Indexed Object"
            self.outputs[0].collection = False
        elif self.return_type == "NAME" and (not len(self.inputs) or self.inputs[0].sn_type != "STRING"):
            self.inputs.clear()
            self.add_string_input("Name")
            self.outputs[0].name = "Named Object"
            self.outputs[0].collection = False
        if self.outputs[0].is_linked:
            self.outputs[0].links[0].to_node.on_link_insert(self.outputs[0].links[0])
    
    
    return_type: bpy.props.EnumProperty(items=[("ALL","All","All Objects"),
                                               ("INDEX","Index","Object by name"),
                                               ("NAME","Name","Object by name")],
                                        name="Return Type",
                                        description="The type of returned object",
                                        update=update_return)
    

    def on_create(self,context):
        out = self.add_blend_data_output("All Objects")
        out.data_type = "Object"
        out.collection = True
        
        
    def draw_node(self,context,layout):
        layout.prop(self,"return_type",expand=True)


    def code_evaluate(self, context, touched_socket):

        limiter = ""
        if self.return_type != "ALL":
            limiter = f"[{self.inputs[0].value}]"

        return {
            "code": f"bpy.data.objects{limiter}"
        }