from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
import bpy


class SNA_Node_None(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_None"
    bl_label = "None"

    def update_value(self, context):
        self._generate()

    def on_create(self):
        self.add_output("ScriptingDataSocket", label="None")

    def generate(self):
        self.outputs[0].code = f"None"
