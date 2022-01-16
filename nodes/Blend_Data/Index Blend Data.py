from pickle import TUPLE
import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_IndexBlendDataNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_IndexBlendDataNode"
    bl_label = "Index Blend Data"
    node_color = "BLEND_DATA"
    
    def on_create(self, context):
        inp = self.add_blend_data_input("Blend Data Collection")
        inp.subtype = "COLLECTION"
        inp.required = True
        self.add_integer_input("Index")
        self.add_blend_data_output("Blend Data")

    def update_index_type(self, context):
        self.convert_socket(self.inputs[1], self.socket_names[self.index_type])
        self._evaluate(context)
        
    index_type: bpy.props.EnumProperty(name="Index Type",
                                description="The type of index to use",
                                items=[("Integer", "Index", "Starts at 0. Negative indices go to the back of the list."),
                                       ("String", "Name", "Refers to the name property of the element.")],
                                update=update_index_type)
        
    def evaluate(self, context):
        self.outputs[0].python_value = f"{self.inputs[0].python_value}[{self.inputs[1].python_value}]"

    def draw_node(self, context, layout):
        layout.prop(self, "index_type", expand=True)