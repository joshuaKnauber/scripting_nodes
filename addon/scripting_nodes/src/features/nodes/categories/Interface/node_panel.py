from scripting_nodes.src.features.nodes.base_node import SNA_BaseNode
import bpy


class SNA_Node_Panel(SNA_BaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_Panel"
    bl_label = "Panel"
    sn_options = {"ROOT_NODE"}

    def on_create(self):
        pass

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
                    self.layout.label(text="testing")
        """
