import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_ChangeFrameNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_ChangeFrameNode"
    bl_label = "On Frame Change"
    is_trigger = True
    bl_width_default = 200

    action: bpy.props.EnumProperty(items=[("frame_change_pre", "Before", "Called after frame change for playback and rendering, before any data is evaluated for the new frame"), ("frame_change_post", "After", "Called after frame change for playback and rendering, after the data has been evaluated for the new frame")],name="Time of Action", description="When you want your event handler to run", update=SN_ScriptingBaseNode._evaluate)

    def on_create(self, context):
        self.add_execute_output()


    def draw_node(self,context,layout):
        row = layout.row()
        row.scale_y = 1.2
        op = row.operator("sn.run_event",text="Run Event",icon="PLAY")
        op.uid = self.static_uid
        layout.prop(self, "action", expand=True)


    def evaluate(self, context):
        self.code_import = f"from bpy.app.handlers import persistent"
        self.code = f"""
                        @persistent
                        def {self.action}_handler_{self.static_uid}(dummy):
                            {self.indent(self.outputs[0].python_value, 6) if self.outputs[0].python_value else 'pass'}
                        """

        self.code_register = f"""
                    bpy.app.handlers.{self.action}.append({self.action}_handler_{self.static_uid})
                    bpy.context.scene.sn.node_function_cache['{self.static_uid}'] = {self.action}_handler_{self.static_uid}
                    """
        self.code_unregister = f"""
                    bpy.app.handlers.{self.action}.remove({self.action}_handler_{self.static_uid})
                    if '{self.static_uid}' in bpy.context.scene.sn.node_function_cache:
                        del bpy.context.scene.sn.node_function_cache['{self.static_uid}']
                    """
