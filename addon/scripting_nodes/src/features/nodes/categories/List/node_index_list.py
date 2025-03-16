from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
import bpy


class SNA_Node_IndexList(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_IndexList"
    bl_label = "Index List"

    def on_create(self):
        self.add_input("ScriptingListSocket", "List")
        self.add_input("ScriptingIntegerSocket", "Index")
        self.add_output("ScriptingDataSocket", "Item")

    def generate(self):
        list_input = self.inputs["List"].eval() 
        index = self.inputs["Index"].eval()
        self.outputs[0].code = f"{list_input}[{index}]"