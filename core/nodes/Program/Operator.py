import bpy
from ..base_node import SN_BaseNode


class SN_OperatorNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_OperatorNode"
    bl_label = "Operator"

    def on_create(self, context):
        self.add_execute_output()

    def generate(self, context):
        sn = context.scene.sn
        self.code = f"""
            class {sn.info.short_identifier.upper()}_Operator(bpy.types.Operator):
                bl_idname = "{sn.info.short_identifier.lower()}.operator"
                bl_label = "Scripting Node Operator"
                bl_options = {'{"REGISTER", "UNDO"}'}

                def execute(self, context):
                    {self.outputs[0].code_block(5)}
                    return {'{"FINISHED"}'}
        """

    def draw_node(self, context, layout):
        for line in self.code.split("\n"):
            layout.label(text=line)
