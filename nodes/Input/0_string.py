import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_StringNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_StringNode"
    bl_label = "String"
    # bl_icon = "GRAPH"
    bl_width_default = 160

    node_options = {
        "default_color": (0.3,0.3,0.3),
    }

    def update_value(self, context):
        if self.value and self.value[-1] == "\\":
            self["value"] = self.value[:-1] + "/"

    value: bpy.props.StringProperty(name="String Value", update=update_value)

    def on_create(self,context):
        self.add_string_output("String").mirror_name = True

    def draw_node(self,context,layout):
        layout.prop(self, "value", text="")


    def code_evaluate(self, context, touched_socket):

        return {
            "code": f"r\"{self.value}\""
        }