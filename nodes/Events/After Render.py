import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_AfterRenderNode(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_AfterRenderNode"
    bl_label = "On Render Finish"
    is_trigger = True
    bl_width_default = 200

    action: bpy.props.EnumProperty(items=[("render_cancel", "Cancel", "On canceling a render job"), ("render_post", "After", "On render (after)"), ("render_complete", "Complete", "On completion of render job")],name="Time of Action", description="When you want your event handler to run", update=SN_ScriptingBaseNode._evaluate)

    def on_create(self, context):
        self.add_execute_output()


    def draw_node(self,context,layout):
        row = layout.row()
        row.scale_y = 1.2
        op = row.operator("sn.run_event",text="Run Event",icon="PLAY")
        op.handler = self.action
        op.uid = self.static_uid
        op.handler = self.action
        layout.prop(self, "action", expand=True)


    @property
    def handler_name(self):
        return f"{self.action}_handler_{self.static_uid}"

    def evaluate(self, context):
        self.code_import = f"from bpy.app.handlers import persistent"
        self.code = f"""
                        @persistent
                        def {self.handler_name}(dummy):
                            {self.indent(self.outputs[0].python_value, 7) if self.outputs[0].python_value.strip() else 'pass'}
                        """

        self.code_register = f"bpy.app.handlers.{self.action}.append({self.handler_name})"
        self.code_unregister = f"bpy.app.handlers.{self.action}.remove({self.handler_name})"