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
        self.add_execute_input("Execute")
        self.add_boolean_input("Condition")

        self.add_execute_output("Continue")
        self.add_execute_output("Condition True")
        self.add_execute_output("Condition False")

    def code_evaluate(self, context, touched_socket):

        return {
            "code": f"""
                    if {self.inputs[1].value}:
                        {self.outputs[1].block(6) if self.outputs[1].block(6) else "pass"}
                    else:
                        {self.outputs[2].block(6) if self.outputs[2].block(6) else "pass"}
                    {self.outputs[0].block(5)}
                    """
        }