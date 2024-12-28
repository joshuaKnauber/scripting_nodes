from scripting_nodes.src.lib.utils.code.format import indent
from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
import bpy


class SNA_Node_Panel(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_Panel"
    bl_label = "Panel"
    sn_options = {"ROOT_NODE"}

    def on_create(self):
        self.add_output("ScriptingInterfaceSocket")

    def generate(self):
        # layout = self.inputs["Interface"].get_meta("layout", "self.layout")

        # self.outputs["Interface"].set_meta("layout", layout)

        self.code = f"""
            import bpy

            class SNA_PT_AddonPanel(bpy.types.Panel):
                bl_idname = "SNA_PT_AddonPanel"
                bl_label = "WORKING GENERATED"
                bl_space_type = 'PROPERTIES'
                bl_region_type = 'WINDOW'
                bl_context = "object"

                def draw(self, context: bpy.types.Context):
                    {indent(self.outputs["Interface"].eval("pass"), 5)}
        """
