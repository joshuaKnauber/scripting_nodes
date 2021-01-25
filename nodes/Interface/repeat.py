import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode



class SN_RepeatLayoutNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_RepeatLayoutNode"
    bl_label = "Repeat - Layout"
    # bl_icon = "GRAPH"
    bl_width_default = 160
    
    node_options = {
        "default_color": (0.3,0.3,0.3),
    }


    def on_create(self,context):
        self.add_interface_input("Interface").mirror_name = True
        self.add_integer_input("Repetitions")

        self.add_dynamic_interface_output("Repeat")
        self.add_integer_output("Step")


    def code_evaluate(self, context, touched_socket):
        if touched_socket == self.inputs[0]:
            return {
                "code": f"""
                        repeat_node_{self.uid} = 0
                        for repeat_node_{self.uid} in range({self.inputs[1].code()}):
                            {self.outputs["Repeat"].by_name(7) if self.outputs["Repeat"].by_name() else "pass"}
                        """
            }
        else:
            return {"code": f"""repeat_node_{self.uid}"""}