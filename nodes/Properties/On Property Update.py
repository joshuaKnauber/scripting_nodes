import bpy
from ..base_node import SN_ScriptingBaseNode
from ..templates.PropertyReferenceNode import PropertyReferenceNode



class SN_OnPropertyUpdateNode(bpy.types.Node, SN_ScriptingBaseNode, PropertyReferenceNode):

    bl_idname = "SN_OnPropertyUpdateNode"
    bl_label = "On Property Update"
    node_color = "PROGRAM"
    bl_width_default = 240
    is_trigger = True
    

    def on_create(self, context):
        self.add_execute_output()
        self.add_data_output("Value")
        self.add_property_output("Attached To Item")
        self.ref_ntree = self.node_tree
        
        
    def update_func_name(self, prop):
        return f"sna_update_{prop.python_name}_{self.static_uid}"
    
    
    def update_nodes_with_props(self):
        # update all nodes with properties when this node changes
        for ntree in bpy.data.node_groups:
            if ntree.bl_idname == "ScriptingNodesTree":
                for node in ntree.nodes:
                    if hasattr(node, "properties"):
                        node._evaluate(bpy.context)
    
    
    def on_ref_prop_change(self, context):
        self.update_nodes_with_props()
    
    def on_free(self):
        self.update_nodes_with_props()
        
    def on_copy(self, old):
        self.update_nodes_with_props()
        

    def evaluate(self, context):        
        prop_src = self.get_prop_source()
        if prop_src and self.prop_name in prop_src.properties and not prop_src.properties[self.prop_name].property_type in ["Group", "Collection"]:
            prop = prop_src.properties[self.prop_name]
            
            self.outputs["Attached To Item"].python_value = f"self"
            self.outputs["Value"].python_value = "sna_updated_prop"
            
            self.code_imperative = f"""
                def {self.update_func_name(prop)}(self, context):
                    sna_updated_prop = self.{prop.python_name}
                    {self.indent(self.outputs[0].python_value, 5)}
                """
        else:
            self.outputs["Attached To Item"].reset_value()
            self.outputs["Value"].reset_value()


    def draw_node(self, context, layout):
        self.draw_reference_selection(layout)
        prop_src = self.get_prop_source()
        if self.prop_name and prop_src and self.prop_name in prop_src.properties:
            prop = prop_src.properties[self.prop_name]
            if prop.property_type in ["Group", "Collection"]:
                self.draw_warning(layout, "Can't update group properties!")
        else:
            self.draw_warning(layout, "No Property selected!")