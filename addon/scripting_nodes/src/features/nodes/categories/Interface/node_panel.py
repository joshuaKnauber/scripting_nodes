from scripting_nodes.src.features.nodes.base_node import SNA_BaseNode
import bpy


class SNA_Node_Panel(SNA_BaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_Panel"
    bl_label = "Panel"

    def on_create(self):
        pass

    def generate(self):
        pass
        # layout = self.inputs["Interface"].get_meta("layout", "self.layout")
        # self.code = f"""
        #     {layout}.label(text={self.inputs['Label'].get_code()})
        #     {self.outputs["Interface"].get_code(3)}
        # """

        # self.outputs["Interface"].set_meta("layout", layout)
