import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_IsNoneNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_IsNoneNode"
    bl_label = "Data Is None"
    # bl_icon = "GRAPH"
    bl_width_default = 160

    node_options = {
        "default_color": (0.3,0.3,0.3),
    }

    def on_create(self,context):
        self.add_blend_data_input("Blend Data").mirror_name = True
        self.add_boolean_output("Is None")


    def code_evaluate(self, context, touched_socket):

        return {
            "code": f"""{self.inputs[0].code()} == None"""
        }