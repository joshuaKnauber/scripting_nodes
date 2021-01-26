import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode



class SN_IfLayoutNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_IfLayoutNode"
    bl_label = "If/Else - Layout"
    # bl_icon = "GRAPH"
    bl_width_default = 160
    
    node_options = {
        "default_color": (0.3,0.3,0.3),
    }


    def on_create(self,context):
        self.add_interface_input("Interface").mirror_name = True
        self.add_boolean_input("Condition")

        self.add_dynamic_interface_output("True")
        self.add_dynamic_interface_output("False")
    

    def code_evaluate(self, context, touched_socket):
        
        return {
            "code": f"""
                    if {self.inputs[1].code()}:
                        {self.outputs["True"].by_name(6) if self.outputs["True"].by_name().strip() else "pass"}
                    else:
                        {self.outputs["False"].by_name(6) if self.outputs["False"].by_name().strip() else "pass"}
                    """
        }

    def what_layout(self,socket):
        return self.inputs[0].links[0].from_node.what_layout(self.inputs[0])