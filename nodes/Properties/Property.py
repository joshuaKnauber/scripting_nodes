import bpy
from ..base_node import SN_ScriptingBaseNode
from ..templates.PropertyReferenceNode import PropertyReferenceNode



class SN_PropertyNode(bpy.types.Node, SN_ScriptingBaseNode, PropertyReferenceNode):

    bl_idname = "SN_PropertyNode"
    bl_label = "Property"
    bl_width_default = 200
    node_color = "PROPERTY"
    
    allow_prop_paste = True
    add_indexing_inputs = True
    

    def on_create(self, context):
        self.add_property_output("Property")
        self.add_data_output("Value")


    def evaluate(self, context):
        # return blender property
        if self.prop_source == "BLENDER":
            if self.pasted_data_path:
                data_path = "bpy"

                inp_index = 0
                data = self.get_data()                    
                for segment in data[:-1]:
                    data_path += f".{segment.split('[')[0]}"
                    
                    if self.segment_is_indexable(segment):
                        if self.inputs[inp_index].index_type == "Property":
                            data_path = self.inputs[inp_index].python_value_pointer
                        else:
                            data_path += f"[{self.inputs[inp_index].python_value}]"
                        inp_index += 1
                    
                self.outputs["Property"].python_value = f"({data_path}, '{data[-1]}')"
                self.outputs["Value"].python_value = f"{data_path}.{data[-1]}"
            else:
                self.outputs["Property"].reset_value()
                self.outputs["Value"].reset_value()
        
        # return custom property
        else:
            prop_src = self.get_prop_source()
            # valid property selected
            if prop_src and self.prop_name in prop_src.properties and not prop_src.properties[self.prop_name].property_type in ["Group", "Collection"]:
                prop = prop_src.properties[self.prop_name]
                self.outputs["Property"].python_value = f"(bpy.data.scenes[{self.inputs['Index'].python_value}], '{prop.python_name}')"
                self.outputs["Value"].python_value = f"bpy.data.scenes[{self.inputs['Index'].python_value}].{prop.python_name}"
            # no valid property selected
            else:
                self.outputs["Property"].reset_value()
                self.outputs["Value"].reset_value()

    def draw_node(self, context, layout):
        self.draw_reference_selection(layout)
        if self.prop_source != "BLENDER":
            prop_src = self.get_prop_source()
            if self.prop_name and prop_src and self.prop_name in prop_src.properties:
                if prop_src.properties[self.prop_name].property_type in ["Group", "Collection"]:
                    self.draw_warning(layout, "Can't return Group or Collection properties!")
