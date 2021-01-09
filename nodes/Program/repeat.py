import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_RepeatProgramNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_RepeatProgramNode"
    bl_label = "Repeat - Program"
    # bl_icon = "GRAPH"
    bl_width_default = 160

    node_options = {
        "default_color": (0.3,0.3,0.3),
    }

    def on_create(self,context):
        self.add_execute_input("Execute")
        self.add_integer_input("Repetitions")

        self.add_execute_output("Continue")
        self.add_execute_output("Repeat")
        self.add_integer_output("Step")

    def code_evaluate(self, context, touched_socket):

        if touched_socket == self.inputs[0]:
            return {
                "code": f"""
                        repeat_node_{self.uid} = 0
                        for repeat_node_{self.uid} in range({self.inputs[1].code()}):
                            {self.outputs[1].code(7) if self.outputs[1].code(0) else "pass"}
                        {self.outputs[0].code(5)}
                        """
            }
        else:
            return {"code": f"""repeat_node_{self.uid}"""}