from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
import bpy


class SNA_Node_CombineStrings(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_CombineStrings"
    bl_label = "Combine Strings"

    def on_create(self):
        self.add_input("ScriptingStringSocket", label="Separator")
        self.add_input("ScriptingStringSocket", label="String")
        self.add_input("ScriptingStringSocket", label="String", dynamic=True)
        self.add_output("ScriptingStringSocket", label="Combined")

    def generate(self):
        sockets = self.inputs[1:-1]
        inputs = [inp.eval() for inp in sockets]
        self.outputs[0].code = f"{self.inputs[0].eval()}.join([{', '.join(inputs)}])"
