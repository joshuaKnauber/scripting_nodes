from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
import bpy


class SNA_Node_SortList(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_SortList"
    bl_label = "Sort List"

    def on_create(self):
        self.add_input("ScriptingListSocket", "List")
        self.add_input("ScriptingBooleanSocket", "Reverse")
        self.add_output("ScriptingListSocket", "Sorted List")

    def generate(self):
        list_input = self.inputs["List"].eval()
        reverse = self.inputs["Reverse"].eval()
        self.outputs[0].code = f"sorted({list_input}, reverse={reverse})"