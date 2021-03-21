import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode



class SN_OtherDataNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_OtherDataNode"
    bl_label = "Other Scene Data"
    # bl_icon = "GRAPH"
    bl_width_default = 160
    
    node_options = {
        "default_color": (0.3,0.3,0.3),
    }
    
    
    def data_items(self,context):
        types = ["brushes","cache_files","cameras", "fonts","grease_pencils",
                "lattices","libraries","lightprobes","linestyles","masks",
                "movieclips","paint_curves","palettes","particles","scenes","screens","shape_keys",
                "sounds","speakers","volumes","window_managers"]
        items = []
        for item in types:
            items.append((item,item.replace("_"," ").title(),item))
        return items
    
    
    def update_type(self,context):
        self.outputs[0].data_type = self.get_type()
        self.outputs[0].data_type_collection = self.get_srna()
        self.outputs[0].data_identifier = self.data_type
        self.outputs[0].data_name = self.data_type.replace("_"," ").title()
        for link in self.outputs[0].links:
            link.to_socket.node.on_link_insert(link)
        self.auto_compile()

    
    data_type: bpy.props.EnumProperty(items=data_items,
                                      update=update_type,
                                      name="Data",
                                      description="Data Type that will be returned")
    
    def get_type(self):
        return eval("bpy.data.bl_rna.properties[\""+self.data_type+"\"].fixed_type.identifier")

    def get_srna(self):
        if eval("bpy.data.bl_rna.properties[\""+self.data_type+"\"].srna"):
            return eval("bpy.data.bl_rna.properties[\""+self.data_type+"\"].srna.identifier")
        return ""
    
    def update_return(self,context):
        if self.return_type == "ALL" and len(self.inputs):
            self.inputs.clear()
            self.outputs[0].default_text = "All"
            self.outputs[0].subtype = "COLLECTION"
        elif self.return_type == "INDEX" and (not len(self.inputs) or self.inputs[0].socket_type != "INTEGER"):
            self.inputs.clear()
            self.add_integer_input("Index").set_default(0)
            self.outputs[0].default_text = "By Index"
            self.outputs[0].subtype = "NONE"
        elif self.return_type == "NAME" and (not len(self.inputs) or self.inputs[0].socket_type != "STRING"):
            self.inputs.clear()
            self.add_string_input("Name")
            self.outputs[0].default_text = "By Name"
            self.outputs[0].subtype = "NONE"
        for link in self.outputs[0].links:
            link.to_socket.node.on_link_insert(link)
    
    
    return_type: bpy.props.EnumProperty(items=[("ALL","All","All"),
                                               ("INDEX","Index","By index"),
                                               ("NAME","Name","By name")],
                                        name="Return Type",
                                        description="The type of returned object",
                                        update=update_return)
    

    def on_create(self,context):
        out = self.add_blend_data_output("All")
        out.data_type = self.get_type()
        out.data_type_collection = self.get_srna()
        out.data_identifier = self.data_type
        out.data_name = self.data_type.replace("_"," ").title()
        out.subtype = "COLLECTION"
        
        
    def draw_node(self,context,layout):
        layout.prop(self,"data_type",text="")
        layout.prop(self,"return_type",expand=True)


    def code_evaluate(self, context, touched_socket):

        limiter = ""
        if self.return_type != "ALL":
            limiter = f"[{self.inputs[0].code()}]"

        return {
            "code": f"bpy.data.{self.outputs[0].data_identifier}{limiter}"
        }