import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_ScriptNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_ScriptNode"
    bl_label = "Script"
    # bl_icon = "GRAPH"
    bl_width_default = 200

    node_options = {
        "default_color": (0.2,0.2,0.2),
        "starts_tree": True
    }
    
    
    placement: bpy.props.EnumProperty(items=[("IMPERATIVE","Imperative","Run this in the imperative code section, when blender loads the script file"),
                                             ("REGISTER", "Register","Run this when your addon is being registered"),
                                             ("UNREGISTER", "Unregister","Run this when your addon is being unregistered")],
                                      name="Placement",
                                      description="Placement of the generated code from the connected nodes",
                                      update=SN_ScriptingBaseNode.auto_compile)


    def on_create(self,context):
        self.add_execute_output("Script")
        
        
    def draw_node(self, context, layout):
        if hasattr(self, "placement"):
            layout.prop(self,"placement",expand=True)
            
            
    def code_register(self, context):
        if hasattr(self,"placement") and self.placement == "REGISTER":
            return {
                "code": f"""
                        {self.outputs[0].code(6)}
                        """
            }
            
            
    def code_unregister(self, context):
        if hasattr(self,"placement") and self.placement == "UNREGISTER":
            return {
                "code": f"""
                        {self.outputs[0].code(6)}
                        """
            }


    def code_evaluate(self, context, touched_socket):
        if not hasattr(self,"placement") or (hasattr(self, "placement") and self.placement == "IMPERATIVE"):
            return {
                "code": f"""
                        {self.outputs[0].code(6)}
                        """
            }