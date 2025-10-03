from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
import bpy


class SNA_Node_AddonInfo(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_AddonInfo"
    bl_label = "Addon Info"

    def on_create(self):
        self.add_output("ScriptingStringSocket", label="Addon Name")

    def generate(self):
        # In dev mode, output reference to the scene property
        # In production/export mode, output the literal string value
        if bpy.context.scene.sna.addon.build_with_production_code:
            self.outputs[0].code = f"'{bpy.context.scene.sna.addon.addon_name}'"
        else:
            self.outputs[0].code = "bpy.context.scene.sna.addon.addon_name"
