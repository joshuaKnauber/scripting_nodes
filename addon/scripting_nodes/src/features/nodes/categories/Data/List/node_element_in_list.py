from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
import bpy


class SNA_Node_ElementInList(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_ElementInList"
    bl_label = "Element In List"

    def on_create(self):
        self.add_input("ScriptingListSocket", "List")
        self.add_input("ScriptingDataSocket", "Element")
        self.add_output("ScriptingIntegerSocket", "Index")
        self.add_output("ScriptingBooleanSocket", "Is In List")

    def generate(self):
        list_input = self.inputs["List"].eval()
        element = self.inputs["Element"].eval()
        self.outputs["Index"].code = f"{list_input}.index({element})"
        self.outputs["Is In List"].code = f"{element} in {list_input}"