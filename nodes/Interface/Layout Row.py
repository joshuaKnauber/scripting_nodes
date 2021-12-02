import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_LayoutRowNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_LayoutRowNode"
    bl_label = "Row"
    layout_type = "row"
    node_color = "INTERFACE"

    def on_create(self, context):
        self.add_interface_input()
        self.add_interface_output()
        self.add_dynamic_interface_output()

    def evaluate(self, context):
        self.code = f"""
                    row = {self.active_layout}.row()
                    {self.indent([out.python_value for out in self.outputs[:-1]], 5)}
                    """

    def draw_node(self, context, layout):
        pass