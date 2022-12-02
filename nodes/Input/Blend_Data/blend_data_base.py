import bpy



class BlendDataBaseNode():

    data_type = ""
    data_type_plural = ""
    
    active_path = ""
    data_path = ""
    
    node_color = "PROPERTY"
    
    def on_create(self, context):
        self.add_collection_property_output(f"All {self.data_type_plural}")
        if self.active_path: self.add_property_output(f"Active {self.data_type}")
        self.add_property_output("Indexed")
        self.add_integer_input("Index")

    def update_index_type(self, context):
        inp = self.convert_socket(self.inputs[0], self.socket_names[self.index_type])
        inp.name = "Index" if self.index_type == "Integer" else "Name"
        self._evaluate(context)
        
    index_type: bpy.props.EnumProperty(name="Index Type",
                                description="The type of index to use",
                                items=[("Integer", "Index", "Starts at 0. Negative indices go to the back of the list."),
                                       ("String", "Name", "Refers to the name property of the element.")],
                                update=update_index_type)
        
    def evaluate(self, context):
        self.outputs[f"All {self.data_type_plural}"].python_value = self.data_path
        if self.active_path: self.outputs[f"Active {self.data_type}"].python_value = self.active_path
        self.outputs["Indexed"].python_value = f"{self.data_path}[{self.inputs[0].python_value}]"

    def draw_node(self, context, layout):
        layout.prop(self, "index_type", expand=True)