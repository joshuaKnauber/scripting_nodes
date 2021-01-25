import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_IfProgramNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_IfProgramNode"
    bl_label = "If/Else - Program"
    # bl_icon = "GRAPH"
    bl_width_default = 160

    node_options = {
        "default_color": (0.3,0.3,0.3),
    }

    def on_create(self,context):
        self.add_execute_input("If/Else")
        self.add_boolean_input("Condition")

        self.add_execute_output("Continue")
        self.add_execute_output("True")
        self.add_execute_output("False")

    def code_evaluate(self, context, touched_socket):

        return {
            "code": f"""
                    if {self.inputs[1].code()}:
                        {self.outputs[1].code(6) if self.outputs[1].code().strip() else "pass"}
                    else:
                        {self.outputs[2].code(6) if self.outputs[2].code().strip() else "pass"}
                    {self.outputs[0].code(5)}
                    """
        }