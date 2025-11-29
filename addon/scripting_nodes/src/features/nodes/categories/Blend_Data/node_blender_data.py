from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
from scripting_nodes.src.lib.utils.sockets.modify import update_socket_type
import bpy

class SNA_Node_BlendDataBlenderData(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_BlendDataBlenderData"
    bl_label = "Blender Data"

    def on_create(self):
        self.add_output("ScriptingBlendDataSocket", "Current Context")
        self.add_output("ScriptingBlendDataSocket", "Blend Data")
        self.add_output("ScriptingBlendDataSocket", "App")
        self.add_output("ScriptingBlendDataSocket", "Path")

    def generate(self):
        self.outputs["Current Context"].code = f"bpy.context"
        self.outputs["Blend Data"].code = f"bpy.data"
        self.outputs["App"].code = f"bpy.app"
        self.outputs["Path"].code = f"bpy.path"
