import bpy
from ...base_node import SN_ScriptingBaseNode



class SN_ForInterfaceNode(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_ForInterfaceNode"
    bl_label = "Loop For (Interface) (Legacy)"
    bl_width_default = 200
    node_color = "INTERFACE"
    
    passthrough_layout_type = True
    
    def on_create(self, context):
        self.add_interface_input()
        self.add_collection_property_input("Collection")
        self.add_interface_output("Repeat")
        self.add_interface_output("Continue")
        self.add_property_output("Item").changeable = True
        self.add_integer_output("Index")
        
        
    def update_type(self, context):
        inp = self.convert_socket(self.inputs[1], self.socket_names[self.for_type])
        inp.name = self.for_type
        self.convert_socket(self.outputs["Item"], self.socket_names["Data"] if self.for_type == "List" else self.socket_names["Property"])
        self._evaluate(context)
        
    for_type: bpy.props.EnumProperty(name="Type",
                                description="Collection Type",
                                items=[("List", "List", "List"),
                                       ("Collection", "Collection", "Collection")],
                                default="Collection",
                                update=update_type)

    reverse: bpy.props.BoolProperty(name="Reverse",
                                description="Reverse the order the loop runs through the items",
                                default=False,
                                update=SN_ScriptingBaseNode._evaluate)

    def evaluate(self, context):
        if self.inputs[1].is_linked:
            self.outputs["Index"].python_value = f"i_{self.static_uid}"
            self.outputs["Item"].python_value = f"{self.inputs[1].python_value}[i_{self.static_uid}]"
            self.code = f"""
                        for i_{self.static_uid} in range({f"len({self.inputs[1].python_value})" if not self.reverse else f"len({self.inputs[1].python_value})-1,-1,-1"}):
                            {self.indent(self.outputs['Repeat'].python_value, 7) if self.outputs['Repeat'].python_value.strip() else 'pass'}
                        {self.indent(self.outputs['Continue'].python_value, 6)}
                        """
        else:
            self.code = f"""
                        {self.active_layout}.label(text='No Collection connected!', icon='ERROR')
                        {self.indent(self.outputs['Continue'].python_value, 6)}
                        """
            self.outputs["Index"].reset_value()
            self.outputs["Item"].reset_value()
            
    def draw_node(self, context, layout):
        layout.prop(self, "for_type")
        layout.prop(self, "reverse")