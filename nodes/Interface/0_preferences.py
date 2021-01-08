import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode



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


    def on_create(self,context):
        self.add_interface_output("Preferences")
        self.add_dynamic_interface_output("Preferences")
    

    def code_evaluate(self, context, touched_socket):
        
        if self.addon_tree.doing_export:
            return {
                "code": f"""
                        class SNA_AddonPreferences_{self.uid}(bpy.types.AddonPreferences):
                            bl_idname = __name__.partition('.')[0]
                            
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
            
            
    def draw_node(self,context,layout):
        if len(self.collection.items) > 1:
            row = layout.row()
            row.alert = True
            row.label(text="You have multiple addon preferences",icon="ERROR")
        
    
    def code_register(self, context): 
        if self.addon_tree.doing_export:
            return {
                "code": f"""
                        bpy.utils.register_class(SNA_AddonPreferences_{self.uid})
                        
                        """
            }
        
    
    def code_unregister(self, context):
        if self.addon_tree.doing_export:
            return {
                "code": f"""
                        bpy.utils.unregister_class(SNA_AddonPreferences_{self.uid})
                        
                        """
            }