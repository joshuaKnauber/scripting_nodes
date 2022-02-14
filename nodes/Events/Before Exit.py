import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_BeforeExitNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_BeforeExitNode"
    bl_label = "On Exit"
    is_trigger = True
    bl_width_default = 200


    def on_create(self, context):
        self.add_execute_output()


    def draw_node(self,context,layout):
        row = layout.row()
        row.scale_y = 1.2
        op = row.operator("sn.run_event",text="Run Event",icon="PLAY")
        op.uid = self.static_uid


    def evaluate(self, context):
        self.code_import = f"import atexit"
        self.code = f"""
                        def before_exit_handler_{self.static_uid}(dummy):
                            {self.indent(self.outputs[0].python_value, 6) if self.outputs[0].python_value else 'pass'}
                        """

        self.code_register = f"""
                    atexit.register(before_exit_handler_{self.static_uid})
                    bpy.context.scene.sn.node_function_cache['{self.static_uid}'] = before_exit_handler_{self.static_uid}
                    """
        self.code_unregister = f"""
                    atexit.unregister(before_exit_handler_{self.static_uid})
                    if '{self.static_uid}' in bpy.context.scene.sn.node_function_cache:
                        del bpy.context.scene.sn.node_function_cache['{self.static_uid}']
                    """
