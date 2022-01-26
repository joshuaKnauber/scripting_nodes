import bpy
from ..base_node import SN_ScriptingBaseNode
from ..templates.PropertyReferenceNode import PropertyReferenceNode



class SN_PropertyNode(bpy.types.Node, SN_ScriptingBaseNode, PropertyReferenceNode):

    bl_idname = "SN_PropertyNode"
    bl_label = "Property"
    bl_width_default = 200
    

    def on_create(self, context):
        self.add_property_output("Property")
        self.add_data_output("Value")
        inp = self.add_integer_input("Index")
        inp.indexable = True
        inp.index_type = "Integer"


    def evaluate(self, context):
        prop_src = self.get_prop_source()
        if prop_src and self.prop_name in prop_src.properties:
            prop = prop_src.properties[self.prop_name]
            self.outputs["Property"].python_value = ""
            self.outputs["Value"].python_value = f"bpy.context.scene.{prop.python_name}"
        else:
            self.outputs["Property"].reset_value()
            self.outputs["Value"].reset_value()

    def draw_node(self, context, layout):
        self.draw_reference_selection(layout)