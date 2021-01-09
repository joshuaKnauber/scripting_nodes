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
        types = ["brushes","cache_files","cameras", "curves","fonts","grease_pencils",
                "lattices","libraries","lightprobes","linestyles","masks","metaballs",
                "movieclips","paint_curves","palettes","particles","scenes","screens","shape_keys",
                "sounds","speakers","volumes","window_managers"]
        items = []
        for item in types:
            items.append((item,item.replace("_"," ").title(),item))
        return items
    
    
    def update_type(self,context):
        self.outputs[0].data_type = self.get_type()
        self.outputs[0].data_path = "bpy.data." + self.data_type
        if self.outputs[0].is_linked:
            self.outputs[0].links[0].to_node.on_link_insert(self.outputs[0].links[0])
    
    
    data_type: bpy.props.EnumProperty(items=data_items,
                                      update=update_type,
                                      name="Data",
                                      description="Data Type that will be returned")
    
    def get_type(self):
        return eval("bpy.data.bl_rna.properties[\""+self.data_type+"\"].fixed_type.name")
    
    def update_return(self,context):
        if self.return_type == "ALL" and len(self.inputs):
            self.inputs.clear()
            self.outputs[0].default_text = "All"
            self.outputs[0].subtype = "COLLECTION"
        elif self.return_type == "INDEX" and (not len(self.inputs) or self.inputs[0].socket_type != "INTEGER"):
            self.inputs.clear()
            self.add_integer_input("Index").set_default(0)
            self.outputs[0].default_text = "By Index"
            self.outputs[0].subtype = "DATA_BLOCK"
        elif self.return_type == "NAME" and (not len(self.inputs) or self.inputs[0].socket_type != "STRING"):
            self.inputs.clear()
            self.add_string_input("Name")
            self.outputs[0].default_text = "By Name"
            self.outputs[0].subtype = "DATA_BLOCK"
        if self.outputs[0].is_linked:
            self.outputs[0].links[0].to_node.on_link_insert(self.outputs[0].links[0])
    
    
    return_type: bpy.props.EnumProperty(items=[("ALL","All","All"),
                                               ("INDEX","Index","By index"),
                                               ("NAME","Name","By name")],
                                        name="Return Type",
                                        description="The type of returned object",
                                        update=update_return)
    

    def on_create(self,context):
        out = self.add_blend_data_output("All")
        out.data_type = self.get_type()
        out.data_path = "bpy.data." + self.data_type
        out.subtype = "COLLECTION"
        
        
    def draw_node(self,context,layout):
        layout.prop(self,"data_type",text="")
        layout.prop(self,"return_type",expand=True)


    def code_evaluate(self, context, touched_socket):

        limiter = ""
        if self.return_type != "ALL":
            limiter = f"[{self.inputs[0].code()}]"

        return {
            "code": f"{self.outputs[0].data_path}{limiter}"
        }