import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_BranchNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_BranchNode"
    bl_label = "Switch Data"
    # bl_icon = "GRAPH"
    bl_width_default = 160

    node_options = {
        "default_color": (0.3,0.3,0.3),
        "imperative_once": True
    }


    def on_create(self,context):
        self.add_boolean_input("Condition")
        self.add_data_input("True")
        self.add_data_input("False")
        self.add_data_output("Result")


    def code_evaluate(self, context, touched_socket):

        return {
            "code": f"""sn_branch({self.inputs[1].code()},{self.inputs[2].code()},{self.inputs[0].code()})"""
        }