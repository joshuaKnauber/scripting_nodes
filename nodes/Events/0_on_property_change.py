import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_PropertyChangeNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_PropertyChangeNode"
    bl_label = "On Property Change"
    # bl_icon = "GRAPH"
    bl_width_default = 160

    node_options = {
        "default_color": (0.2,0.2,0.2),
        "starts_tree": True
    }
    
    
    selected: bpy.props.StringProperty(name="Property",
                                       description="Selected Property")
    

    def on_create(self,context):
        self.add_execute_output("On Change")


    def draw_node(self,context,layout):
        layout.prop_search(self,"selected",self.addon_tree,"sn_properties",text="")
#TODO