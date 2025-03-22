from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
import bpy


class SNA_Node_Blender_Version(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_Blender_Version"
    bl_label = "Blender Version"


    def on_create(self):
        self.add_output("ScriptingStringSocket", label="Blender Version")

    def generate(self):
        self.outputs[0].code = f'"{bpy.app.version_string}"'
 
