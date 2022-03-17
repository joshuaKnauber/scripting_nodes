import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_GetPropertyScriptlineNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_GetPropertyScriptlineNode"
    bl_label = "Get Property Scriptline"
    bl_width_default = 200

    def on_create(self, context):
        self.add_property_input()
        self.add_property_output()
        
    property_name: bpy.props.StringProperty(name="Property",
                                    description="The name of the property you want to get",
                                    update=SN_ScriptingBaseNode._evaluate)
        
    def evaluate(self, context):
        if self.property_name[0] == "[":
            self.outputs[0].python_value = f"{self.inputs[0].python_value}{self.property_name}"
        else:
            self.outputs[0].python_value = f"{self.inputs[0].python_value}.{self.property_name}"
        
    def draw_node(self, context, layout):
        layout.prop(self, "property_name")