import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_SwitchIconsNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_SwitchIconsNode"
    bl_label = "Switch Icons"
    # bl_icon = "GRAPH"
    bl_width_default = 160

    node_options = {
        "default_color": (0.3,0.3,0.3),
    }

    def on_create(self,context):
        self.add_boolean_input("Switch")
        self.add_icon_input("Icon 1")
        self.add_icon_input("Icon 2")
        self.add_icon_output("Icon")

    def code_evaluate(self, context, touched_socket):

        return {
            "code": f"""{self.inputs[1].code()} if {self.inputs[0].code()} else {self.inputs[2].code()}"""
        }


#TODO convert selected nodes to function
#TODO take expected input with 0 index as default in blend data inputs