from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
import bpy


class SNA_Node_ListLength(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_ListLength"
    bl_label = "List Length"

    def on_create(self):
        self.add_input("ScriptingListSocket", "List")
        self.add_output("ScriptingIntegerSocket", "Length")

    def generate(self):
        list_input = self.inputs["List"].eval()
        self.outputs[0].code = f"len({list_input})"