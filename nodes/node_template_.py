"""
import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode



class SN_YourNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_YourNode"
    bl_label = "Node Name"

    def on_create(self, context):
        self.add_string_output()

    def evaluate(self, context):
        print(self.string)

    string: bpy.props.StringProperty(name="String", description="String value of this node", update=evaluate)

    def draw_node(self, context, layout):
        layout.prop(self, "string", text="")
"""