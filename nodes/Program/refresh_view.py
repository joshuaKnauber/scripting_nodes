import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_RefreshViewNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_RefreshViewNode"
    bl_label = "Refresh View"
    # bl_icon = "GRAPH"
    bl_width_default = 160

    node_options = {
        "default_color": (0.3,0.3,0.3),
        "imperative_once": True
    }

    def on_create(self,context):
        self.add_execute_input("Execute")
        self.add_execute_output("Execute")
        
        
    def code_imperative(self,context):
        
        return {
            "code": f"""
                    def sn_redraw():
                        if bpy.context and bpy.context.screen:
                            for a in bpy.context.screen.areas:
                                a.tag_redraw()
                    """
        }


    def code_evaluate(self, context, touched_socket):
        
        return {
            "code": f"""
                    sn_redraw()
                    """
        }