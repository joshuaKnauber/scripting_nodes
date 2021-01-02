import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode



class SN_GetDataCollectionNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_GetDataCollectionNode"
    bl_label = "Get Data"
    # bl_icon = "GRAPH"
    bl_width_default = 160
    
    node_options = {
        "default_color": (0.3,0.3,0.3),
    }


    current_data_type: bpy.props.StringProperty(default="")
    collection_error: bpy.props.BoolProperty(default=False)


    def on_create(self,context):
        self.add_blend_data_input("Blend Data").copy_name = True
        
        
    def add_data_outputs(self,data_type):
        try:
            for prop in eval(f"bpy.types.{data_type}.bl_rna.properties"):
                if prop.type == "COLLECTION":
                    if hasattr(prop, "fixed_type"):
                        out = self.add_blend_data_output(prop.name,removable=True)
                        out.data_type = prop.fixed_type.identifier
                        out.relative_path = prop.identifier
                        out.collection = True
        except:
            self.outputs.clear()
        
        
    def update_outputs(self,socket):
        self.collection_error = False
        if not socket.data_type:
            self.current_data_type = ""
            self.outputs.clear()
        elif socket.collection:
            self.current_data_type = ""
            self.collection_error = True
        else:
            self.current_data_type = socket.data_type
            if socket.data_type == self.current_data_type and not len(self.outputs):
                self.add_data_outputs(socket.data_type)
            elif socket.data_type != self.current_data_type:
                self.outputs.clear()
                self.add_data_outputs(socket.data_type)
        
        
    def on_link_insert(self,link):
        if link.to_socket == self.inputs[0]:
            self.update_outputs(link.from_socket)
            
            
    def draw_node(self,context,layout):
        if self.collection_error:
            layout.label(text="Connect single data block",icon="ERROR")


    def code_evaluate(self, context, touched_socket):

        return {
            "code": f"{self.inputs[0].value}.{touched_socket.relative_path}"
        }