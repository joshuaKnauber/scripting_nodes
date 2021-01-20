import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode



class SN_SetBlendDataNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_SetBlendDataNode"
    bl_label = "Set Blend Data"
    # bl_icon = "GRAPH"
    bl_width_default = 160
    
    node_options = {
        "default_color": (0.3,0.3,0.3),
    }


    current_data_type: bpy.props.StringProperty(default="")
    collection_error: bpy.props.BoolProperty(default=False)
    no_data_error: bpy.props.BoolProperty(default=False)


    def on_create(self,context):
        self.add_execute_input("Set Blend Data")
        self.add_blend_data_input("Blend Data").mirror_name = True
        self.add_execute_output("Execute").mirror_name = True
        
        
    def add_data_inputs(self,data_type):
        try:
            for prop in eval(f"bpy.types.{data_type}.bl_rna.properties"):
                if prop.type == "POINTER":
                    if hasattr(prop, "identifier") and not prop.name == "RNA":
                        if not prop.is_readonly:
                            inp = self.add_blend_data_input(prop.name)
                            inp.removable = True
                            inp.data_type = prop.fixed_type.identifier
                            inp.data_name = prop.fixed_type.name
                            inp.data_identifier = prop.identifier
            if not len(self.inputs)-2:
                self.no_data_error = True
        except:
            self.remove_input_range(2)
        
        
    def update_inputs(self,socket):
        self.collection_error = False
        self.no_data_error = False
        if socket.subtype == "NONE":
            if socket.data_type == self.current_data_type and not len(self.inputs)-2:
                self.add_data_inputs(socket.data_type)
            elif socket.data_type != self.current_data_type:
                self.remove_input_range(2)
                self.add_data_inputs(socket.data_type)
            self.current_data_type = socket.data_type
        else:
            self.remove_input_range(2)
            self.current_data_type = ""
            self.collection_error = True
        
        
    def on_link_insert(self,link):
        if link.to_socket == self.inputs[1]:
            self.update_inputs(link.from_socket)
            
            
    def draw_node(self,context,layout):
        if self.collection_error:
            layout.label(text="Connect single data block",icon="ERROR")
        elif self.no_data_error:
            layout.label(text="No data found",icon="ERROR")


    def code_evaluate(self, context, touched_socket):

        set_data = []
        for inp in self.inputs[2:]:
            set_data.append(self.inputs[1].code() + "." + inp.data_identifier + "=" + inp.code())

        return {
            "code": f"""
                    {self.list_code(set_data, 5)}
                    {self.outputs[0].code(5)}
            """
        }