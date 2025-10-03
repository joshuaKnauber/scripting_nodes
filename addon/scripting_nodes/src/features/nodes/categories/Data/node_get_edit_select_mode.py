from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
import bpy


class SNA_Node_GetEditSelectMode(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_GetEditSelectMode"
    bl_label = "Get Edit Select Mode"

    def on_create(self):
        self.add_output("ScriptingBooleanSocket", label="Vertex")
        self.add_output("ScriptingBooleanSocket", label="Edge")
        self.add_output("ScriptingBooleanSocket", label="Face")

    def generate(self):
        self.outputs[0].code = f"bpy.context.tool_settings.mesh_select_mode[0]"
        self.outputs[1].code = f"bpy.context.tool_settings.mesh_select_mode[1]"
        self.outputs[2].code = f"bpy.context.tool_settings.mesh_select_mode[2]"