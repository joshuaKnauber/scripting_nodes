import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup

# bpy.app.handlers.frame_change_post
# bpy.app.handlers.frame_change_pre

# bpy.app.handlers.load_post
# bpy.app.handlers.load_pre

# bpy.app.handlers.redo_post
# bpy.app.handlers.redo_pre

# bpy.app.handlers.render_cancel
# bpy.app.handlers.render_complete
# bpy.app.handlers.render_init
# bpy.app.handlers.render_post
# bpy.app.handlers.render_pre

# bpy.app.handlers.undo_post
# bpy.app.handlers.undo_pre


class SN_DephsgraphUpdateNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_DephsgraphUpdateNode"
    bl_label = "Dephsgraph Update Event"
    # bl_icon = "GRAPH"
    bl_width_default = 160

    node_options = {
        "default_color": (0.2,0.2,0.2),
        "starts_tree": True,
        "import_once": True
    }

    action: bpy.props.EnumProperty(items=[("depsgraph_update_pre", "Before", ""), ("depsgraph_update_post", "After", "")],name="Time of Action", description="When you want your event handler to run", update=SN_ScriptingBaseNode.update_needs_compile)

    def on_create(self,context):
        self.add_execute_output("On Dephsgraph Update")


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
                    def depsgraph_update_handler_{self.uid}(dummy):
                        {code if code else "pass"}
                    """
        }

    
    def code_register(self, context):
        return {
            "code": f"""
                    bpy.app.handlers.{self.action}.append(depsgraph_update_handler_{self.uid})
                    """
        }


    def code_unregister(self, context):
        return {
            "code": f"""
                    bpy.app.handlers.{self.action}.remove(depsgraph_update_handler_{self.uid})
                    """
        }