from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
import bpy


class SNA_Node_InvertBoolean(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_InvertBoolean"
    bl_label = "Invert Boolean"

    def on_create(self):
        self.add_input("ScriptingBooleanSocket", "Boolean")
        self.add_output("ScriptingBooleanSocket", "Result")

    def generate(self):
        value = self.inputs["Boolean"].eval()
        self.outputs["Result"].code = f"not {value}"
