from scripting_nodes.src.lib.utils.code.format import indent
from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
import bpy


class SNA_ScriptNode(ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SNA_ScriptNode"
    bl_label = "Script"


    def on_create(self):
        self.add_output("ScriptingProgramSocket")

    def generate(self):
        self.code = indent(self.outputs[0].eval(), 0)