import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_IntegerNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_IntegerNode"
    bl_label = "Integer"
    # bl_icon = "GRAPH"
    bl_width_default = 160

    node_options = {
        "default_color": (0.3,0.3,0.3),
    }

    value: bpy.props.IntProperty(name="Integer Value")

    def on_create(self,context):
        self.add_string_output("Integer").copy_name = True


    def draw_node(self,context,layout):
        layout.prop(self, "value", text="")


    def code_evaluate(self, context, main_tree, touched_socket):

        return {
            "code": f"""{self.value}"""
        }