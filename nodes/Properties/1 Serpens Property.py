import bpy
from ..base_node import SN_ScriptingBaseNode
from ..templates.PropertyReferenceNode import PropertyReferenceNode



class SN_SerpensPropertyNode(bpy.types.Node, SN_ScriptingBaseNode, PropertyReferenceNode):

    bl_idname = "SN_SerpensPropertyNode"
    bl_label = "Serpens Property"
    bl_width_default = 200
    node_color = "PROPERTY"

    add_indexing_inputs = True


    def on_create(self, context):
        self.add_property_output("Property")
        self.add_data_output("Value")
        self.add_property_input("Data")


    def evaluate(self, context):
        prop_src = self.get_prop_source()
        # valid property selected
        if prop_src and self.prop_name in prop_src.properties and not prop_src.properties[self.prop_name].property_type == "Group":
            prop = prop_src.properties[self.prop_name]
            self.outputs["Property"].python_value = f"{self.inputs[0].python_value}.{prop.python_name}"
            self.outputs["Value"].python_value = f"{self.inputs[0].python_value}.{prop.python_name}"
        # no valid property selected
        else:
            self.outputs["Property"].reset_value()
            self.outputs["Value"].reset_value()


    def draw_node(self, context, layout):
        self.draw_reference_selection(layout)
        prop_src = self.get_prop_source()
        if self.prop_name and prop_src and self.prop_name in prop_src.properties:
            if prop_src.properties[self.prop_name].property_type == "Group":
                self.draw_warning(layout, "Can't return Group properties!")
