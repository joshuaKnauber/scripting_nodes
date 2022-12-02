import bpy
from ...base_node import SN_ScriptingBaseNode



class SN_RefreshViewNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_RefreshViewNode"
    bl_label = "Refresh View"
    bl_width_default = 200
    node_color = "PROGRAM"
    
    def on_create(self, context):
        self.add_execute_input()
        self.add_execute_output()

    def evaluate(self, context):
        self.code = f"""
                    if bpy.context and bpy.context.screen:
                        for a in bpy.context.screen.areas:
                            a.tag_redraw()
                    {self.indent(self.outputs[0].python_value, 5)}
                    """