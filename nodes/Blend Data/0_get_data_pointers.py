import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode



class SN_GetDataPointersNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_GetDataPointersNode"
    bl_label = "Get Data"
    # bl_icon = "GRAPH"
    bl_width_default = 160
    
    node_options = {
        "default_color": (0.3,0.3,0.3),
    }


    current_data_type: bpy.props.StringProperty(default="")
    collection_error: bpy.props.BoolProperty(default=False)
    no_data_error: bpy.props.BoolProperty(default=False)


    def on_create(self,context):
        self.add_blend_data_input("Blend Data").mirror_name = True
        
        
    def add_data_outputs(self,data_type):
        try:
            for prop in eval(f"bpy.types.{data_type}.bl_rna.properties"):
                if prop.type == "POINTER":
                    if hasattr(prop, "identifier") and not prop.name == "RNA":
                        out = self.add_blend_data_output(prop.name)
                        out.removable = True
                        out.data_type = prop.fixed_type.identifier
                        out.data_identifier = prop.identifier
            if not len(self.outputs):
                self.no_data_error = True
        except:
            self.outputs.clear()
        
        
    def update_outputs(self,socket):
        self.collection_error = False
        self.no_data_error = False
        if socket.subtype == "DATA_BLOCK":
            if socket.data_type == self.current_data_type and not len(self.outputs):
                self.add_data_outputs(socket.data_type)
            elif socket.data_type != self.current_data_type:
                self.outputs.clear()
                self.add_data_outputs(socket.data_type)
            self.current_data_type = socket.data_type
        else:
            self.outputs.clear()
            self.current_data_type = ""
            self.collection_error = True
        
        
    def on_link_insert(self,link):
        if link.to_socket == self.inputs[0]:
            self.update_outputs(link.from_socket)
            
            
    def draw_node(self,context,layout):
        if self.collection_error:
            layout.label(text="Connect single data block",icon="ERROR")
        elif self.no_data_error:
            layout.label(text="No data found",icon="ERROR")


    def code_evaluate(self, context, touched_socket):

        return {
            "code": f"{self.inputs[0].code()}.{touched_socket.data_identifier}"
        }