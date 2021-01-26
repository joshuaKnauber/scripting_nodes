import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_BooleanNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_BooleanNode"
    bl_label = "Boolean"
    # bl_icon = "GRAPH"
    bl_width_default = 160

    node_options = {
        "default_color": (0.3,0.3,0.3),
    }

    value: bpy.props.BoolProperty(name="Value", update=SN_ScriptingBaseNode.auto_compile)

    def on_create(self,context):
        self.add_boolean_output("Boolean").mirror_name = True


    def draw_node(self,context,layout):
        layout.prop(self, "value")


    def code_evaluate(self, context, touched_socket):

        return {
            "code": f"{self.value}"
        }