import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_RemoveDataNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_RemoveDataNode"
    bl_label = "Remove Blend Data"
    # bl_icon = "GRAPH"
    bl_width_default = 160

    node_options = {
        "default_color": (0.3,0.3,0.3),
    }
    
    
    current_data_type: bpy.props.StringProperty(default="")
    
    
    def add_function_inputs(self, data_type):
        for i in range(len(self.inputs)-1,-1,-1):
            if not i < 2:
                self.inputs.remove(self.inputs[i])


        for data in bpy.data.bl_rna.properties:
            if data.type == "COLLECTION" and type(data.fixed_type).bl_rna.identifier == data_type:
                if "remove" in eval("bpy.data." + data.identifier).bl_rna.functions:

                    for parameter in eval("bpy.data." + data.identifier).bl_rna.functions["remove"].parameters[:-1]:
                        inp = self.add_input_from_prop(parameter)
                        if parameter.type == "ENUM":
                            enum_values = []
                            for item in parameter.enum_items:
                                enum_values.append((item.identifier, item.name, item.description))
                            inp.enum_values = str(enum_values)

                        if not parameter.type in ["POINTER", "COLLECTION"]:
                            inp.set_default(parameter.default)


    def on_link_insert(self, link):
        if link.to_socket == self.inputs[1] and not link.from_socket.data_type == self.current_data_type:
            self.inputs[1].data_type = link.from_socket.data_type
            self.current_data_type = link.from_socket.data_type
            self.add_function_inputs(link.from_socket.data_type)


    def on_create(self,context):
        self.add_execute_input("Execute").copy_name = True
        inp = self.add_blend_data_input("Blend Data")
        inp.subtype = "COLLECTION"
        inp.copy_name = True
        inp.collection = True
        self.add_execute_output("Execute")

    def draw_node(self, context, layout):
        if self.current_data_type:
            layout.label(text="Remove type: " + self.current_data_type)


    def code_evaluate(self, context, touched_socket):
        
        if self.inputs[1].is_linked:
            parameter = ""
            for inp in self.inputs[2:]:
                parameter+=inp.variable_name + "=" + inp.code() + ", "
            return {
                "code": f"""
                        {self.inputs[1].code()}.remove({parameter})
                        {self.outputs[0].code(5)}
                        """
            }

        else:
            return {
                "code": f"""
                        {self.outputs[0].code(5)}
                        """
            }


# Enum socket generation
# Blend data sockets that are not collections
# blend data code return is incorrect