import bpy
import json
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup
from ...node_tree.variables.variables_ui_list import SN_Variable
from ...interface.sidepanel.graph_panels import draw_property
from ...interface.menu.rightclick import construct_from_property



class SN_AddonPreferencesNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_AddonPreferencesNode"
    bl_label = "Addon Preferences"
    # bl_icon = "GRAPH"
    bl_width_default = 200
    
    node_options = {
        "default_color": (0.2,0.2,0.2),
        "starts_tree": True,
        "evaluate_once": True,
        "register_once": True,
        "unregister_once": True,
        "has_collection": True
    }
    
    
    properties: bpy.props.CollectionProperty(type=SN_Variable)
    property_index: bpy.props.IntProperty()


    def on_create(self,context):
        self.add_interface_output("Preferences")
        self.add_dynamic_interface_output("Preferences")
        
        
    def draw_node(self,context,layout):
        if len(self.collection.items) > 1:
            row = layout.row()
            row.alert = True
            row.label(text="You have multiple addon preferences",icon="ERROR")
            
        row = layout.row(align=False)
        row.template_list("SN_UL_VariableList", "Properties", self, "properties", self, "property_index",rows=3)
        col = row.column(align=True)
        col.operator("sn.add_node_property", text="", icon="ADD").node_name = self.name
        col = col.column(align=True)
        col.enabled = bool(len(self.properties))
        col.operator("sn.remove_node_property", text="", icon="REMOVE").node_name = self.name
        col.operator("sn.edit_node_property", text="", icon="GREASEPENCIL").node_name = self.name
        col.operator("sn.get_set_node_property", text="", icon="FORWARD").node_name = self.name
    

    def code_evaluate(self, context, touched_socket):
        
        if self.addon_tree.doing_export:
            property_register = []
            for prop in self.properties:
                property_register.append(prop.property_register())
            return {
                "code": f"""
                        class SNA_AddonPreferences_{self.uid}(bpy.types.AddonPreferences):
                            bl_idname = __name__.partition('.')[0]
                            
                            {self.list_code(property_register, 7)}
                            
                            def draw(self, context):
                                try:
                                    layout = self.layout
                                    {self.outputs["Preferences"].by_name(9)}
                                except Exception as exc:
                                    print(str(exc) + " | Error in {self.label} addon preferences")
                        """
            }
            
        else:
            return {
                "code": f"""
                        def sn_draw_addon_prefs(self):
                            try:
                                layout = self.layout
                                {self.outputs["Preferences"].by_name(8)}
                            except Exception as exc:
                                print(str(exc) + " | Error in {self.label} addon preferences")
                        """
            }
            
    
    def code_register(self, context): 
        property_register = []
        for prop in self.properties:
            property_register.append("bpy.types.SN_AddonPreferences." + prop.property_register().replace(":","="))
                
        if self.addon_tree.doing_export:
            return {
                "code": f"""
                        bpy.utils.register_class(SNA_AddonPreferences_{self.uid})
                        
                        """
            }
            
        else:
            return {
                "code": f"""
                        {self.list_code(property_register, 6)}
                        """
            }
        
    
    def code_unregister(self, context):
        if self.addon_tree.doing_export:
            return {
                "code": f"""
                        bpy.utils.unregister_class(SNA_AddonPreferences_{self.uid})
                        
                        """
            }
            
        else:
            return {
                "code": f"""
                        
                        """
            }