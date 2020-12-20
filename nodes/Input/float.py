import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_FloatNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_FloatNode"
    bl_label = "Float"
    # bl_icon = "GRAPH"
    bl_width_default = 160

    node_options = {
        "default_color": (0.3,0.3,0.3),
    }

    value: bpy.props.FloatProperty(name="Float Value")

    def on_create(self,context):
        self.add_float_output("Float").copy_name = True


    def draw_node(self,context,layout):
        layout.prop(self, "value", text="")


    def code_evaluate(self, context, touched_socket):

        return {
            "code": f"""{self.value}"""
        }