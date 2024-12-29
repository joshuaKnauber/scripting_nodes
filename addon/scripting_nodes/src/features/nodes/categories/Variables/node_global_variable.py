from scripting_nodes.src.lib.utils.code.format import indent
from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
import bpy


class SNA_Node_GlobalVariable(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_GlobalVariable"
    bl_label = "Global Variable"
    sn_options = {"ROOT_NODE"}

    def on_create(self):
        self.add_input("ScriptingStringSocket", "Initial Value")

    def generate(self):
        self.code = f"""
            var_{self.id} = {self.inputs[0].eval()}
        """
