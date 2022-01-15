import bpy



class GetDataNode():
    
    def update_data_type(self, context):
        self.convert_socket(self.outputs[0], self.socket_names[self.data_type])
        if self.data_type == "Blend Data Collection":
            self.outputs[0].subtype = "COLLECTION"
        elif self.data_type == "Blend Data":
            self.outputs[0].subtype = "NONE"
        self._evaluate(context)
        
    data_type: bpy.props.EnumProperty(name="Type",
                                    description="The type of data of this property",
                                    items=[("Data", "Data", "Data"),
                                            ("Blend Data", "Blend Data", "Blend Data"),
                                            ("Blend Data Collection", "Blend Data Collection", "Blend Data Collection"),
                                            ("String", "String", "String"),
                                            ("Boolean", "Boolean", "Boolean"),
                                            ("Boolean Vector", "Boolean Vector", "Boolean Vector"),
                                            ("Float", "Float", "Float"),
                                            ("Float Vector", "Float Vector", "Float Vector"),
                                            ("Integer", "Integer", "Integer"),
                                            ("Integer Vector", "Integer Vector", "Integer Vector"),
                                            ("List", "List", "List")],
                                    update=update_data_type)

    def draw_data_select(self, layout):
        layout.prop(self, "data_type")