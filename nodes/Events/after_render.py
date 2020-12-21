import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_AfterRenderNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_AfterRenderNode"
    bl_label = "After Render"
    # bl_icon = "GRAPH"
    bl_width_default = 180

    node_options = {
        "default_color": (0.2,0.2,0.2),
        "starts_tree": True,
        "import_once": True
    }

    action: bpy.props.EnumProperty(items=[("render_cancel", "Cancel", "On canceling a render job"), ("render_post", "After", "On render (after)"), ("render_complete", "Complete", "On completion of render job")],name="Time of Action", description="When you want your event handler to run", update=SN_ScriptingBaseNode.update_needs_compile)

    def on_create(self,context):
        self.add_execute_output("After Render")


    def draw_node(self,context,layout):
        layout.prop(self, "action", expand=True)


    def code_imports(self, context):
        return {
            "code": f"""from bpy.app.handlers import persistent"""
        }


    def code_imperative(self, context):
        code = self.outputs[0].block(6)

        return {
            "code": f"""
                    @persistent
                    def {self.action}_handler_{self.uid}(dummy):
                        {code if code else "pass"}
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