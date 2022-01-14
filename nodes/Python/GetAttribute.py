import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_GetPropertyScriptlineNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_GetPropertyScriptlineNode"
    bl_label = "Get Property Scriptline"
    bl_width_default = 200

    def on_create(self, context):
        self.add_blend_data_input()
        self.add_string_input("Property")
        self.add_data_output("Data")
        
    def update_data_type(self, context):
        self.convert_socket(self.outputs[0], self.socket_names[self.data_type])
        self._evaluate(context)
        
    data_type: bpy.props.EnumProperty(name="Type",
                                    description="The type of data of this property",
                                    items=[("Data", "Data", "Data"),
                                            ("Blend Data", "Blend Data", "Blend Data"),
                                            ("String", "String", "String"),
                                            ("Boolean", "Boolean", "Boolean"),
                                            ("Boolean Vector", "Boolean Vector", "Boolean Vector"),
                                            ("Float", "Float", "Float"),
                                            ("Float Vector", "Float Vector", "Float Vector"),
                                            ("Integer", "Integer", "Integer"),
                                            ("Integer Vector", "Integer Vector", "Integer Vector"),
                                            ("List", "List", "List")],
                                    update=update_data_type)
        
    def evaluate(self, context):
        self.outputs[0].python_value = f"getattr({self.inputs[0].python_value}, {self.inputs['Property'].python_value}, None)"
        
    def draw_node(self, context, layout):
        layout.prop(self, "data_type")