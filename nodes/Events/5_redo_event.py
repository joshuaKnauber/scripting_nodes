import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_RedoNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_RedoNode"
    bl_label = "On Redo"
    # bl_icon = "GRAPH"
    bl_width_default = 160

    node_options = {
        "default_color": (0.2,0.2,0.2),
        "starts_tree": True,
    }

    action: bpy.props.EnumProperty(items=[("redo_pre", "Before", "On loading a redo step (before)"), ("redo_post", "After", "On loading a redo step (after)")],name="Time of Action", description="When you want your event handler to run", update=SN_ScriptingBaseNode.auto_compile)

    def on_create(self,context):
        self.add_execute_output("On Redo")


    def draw_node(self,context,layout):
        layout.prop(self, "action", expand=True)


    def code_imports(self, context):
        return {
            "code": f"""
                    from bpy.app.handlers import persistent
                    """
        }


    def code_imperative(self, context):
        return {
            "code": f"""
                    @persistent
                    def {self.action}_handler_{self.uid}(dummy):
                        {self.outputs[0].code(6) if self.outputs[0].code().strip() else "pass"}
                    """
        }

    
    def code_register(self, context):
        return {
            "code": f"""
                    bpy.app.handlers.{self.action}.append({self.action}_handler_{self.uid})
                    """
        }


    def code_unregister(self, context):
        return {
            "code": f"""
                    bpy.app.handlers.{self.action}.remove({self.action}_handler_{self.uid})
                    """
        }