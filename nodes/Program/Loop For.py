import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_ForExecuteNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_ForExecuteNode"
    bl_label = "Loop For (Execute)"
    bl_width_default = 200
    node_color = "PROGRAM"
    
    def on_create(self, context):
        self.add_execute_input()
        self.add_list_input("List")
        self.add_execute_output("Repeat")
        self.add_execute_output("Continue")
        self.add_data_output("Item").changeable = True
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
                                update=update_type)
    

    def evaluate(self, context):
        if self.inputs[1].is_linked:
            self.outputs["Index"].python_value = f"i_{self.static_uid}"
            self.outputs["Item"].python_value = f"{self.inputs[1].python_value}[i_{self.static_uid}]"
            self.code = f"""
                        for i_{self.static_uid} in range(len({self.inputs[1].python_value})):
                            {self.indent(self.outputs['Repeat'].python_value, 7) if self.outputs['Repeat'].python_value.strip() else 'pass'}
                        {self.indent(self.outputs['Continue'].python_value, 6)}
                        """
        else:
            self.code = f"""print("No Collection connected to {self.name}!")"""
            self.outputs["Index"].reset_value()
            self.outputs["Item"].reset_value()
            
    def draw_node(self, context, layout):
        layout.prop(self, "for_type")