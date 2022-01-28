import bpy
from ..base_node import SN_ScriptingBaseNode
from ..templates.PropertyReferenceNode import PropertyReferenceNode



class SN_BlenderPropertyNode(bpy.types.Node, SN_ScriptingBaseNode, PropertyReferenceNode):

    bl_idname = "SN_BlenderPropertyNode"
    bl_label = "Blender Property"
    bl_width_default = 200
    node_color = "PROPERTY"
    
    allow_prop_paste = True
    add_indexing_inputs = True
    

    def on_create(self, context):
        self.add_property_output("Property")
        out = self.add_data_output("Value")
        out.changeable = True
        self.prop_source = "BLENDER"


    def evaluate(self, context):
        if self.pasted_data_path:
            data_path = "bpy"

            inp_index = 0
            data = self.get_data()                    
            for segment in data:
                data_path += f".{segment.split('[')[0]}"
                
                if self.segment_is_indexable(segment):
                    if self.inputs[inp_index].bl_label == "Property":
                        data_path = self.inputs[inp_index].python_value
                    else:
                        data_path += f"[{self.inputs[inp_index].python_value}]"
                    inp_index += 1
                
            self.outputs["Property"].python_value = data_path
            self.outputs["Value"].python_value = data_path
        else:
            self.outputs["Property"].reset_value()
            self.outputs["Value"].reset_value()


    def draw_node(self, context, layout):
        self.draw_reference_selection(layout, draw_prop_source=False)