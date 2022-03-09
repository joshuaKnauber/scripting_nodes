import bpy
from ..base_node import SN_ScriptingBaseNode
from ..templates.PropertyReferenceNode import PropertyReferenceNode



class SN_OnPropertyUpdateNode(bpy.types.Node, SN_ScriptingBaseNode, PropertyReferenceNode):

    bl_idname = "SN_OnPropertyUpdateNode"
    bl_label = "On Property Update"
    node_color = "PROGRAM"
    bl_width_default = 250
    is_trigger = True
    

    def on_create(self, context):
        self.add_execute_output()
        self.add_property_output("Attached To Item")
        self.add_property_output("Updated Property")
        self.add_data_output("Property Value").changeable = True
        
        
    def update_func_name(self, prop):
        return f"sna_update_{prop.python_name}_{self.static_uid}"
        

    def evaluate(self, context):        
        prop_src = self.get_prop_source()
        if prop_src and self.prop_name in prop_src.properties and not prop_src.properties[self.prop_name].property_type in ["Group", "Collection"]:
            prop = prop_src.properties[self.prop_name]
            
            self.code = f"""
                def {self.update_func_name(prop)}(self, context):
                    sna_updated_prop = self.{prop.python_name}
                    {self.indent(self.outputs[0].python_value, 5)}
                """
            self.outputs["Updated Property"].python_value = f"self.{prop.python_name}"
            self.outputs["Attached To Item"].python_value = f"self"
            self.outputs["Property Value"].python_value = "sna_updated_prop"
        else:
            self.outputs["Updated Property"].reset_value()
            self.outputs["Attached To Item"].reset_value()
            self.outputs["Property Value"].reset_value()


    def draw_node(self, context, layout):
        self.draw_reference_selection(layout, True)
        prop_src = self.get_prop_source()
        if self.prop_name and prop_src and self.prop_name in prop_src.properties:
            prop = prop_src.properties[self.prop_name]
            if prop.property_type in ["Group", "Collection"]:
                self.draw_warning(layout, "Can't update group properties!")
        else:
            self.draw_warning(layout, "No Property selected!")