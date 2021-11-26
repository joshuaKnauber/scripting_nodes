import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode



class SN_LayoutRowNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_LayoutRowNode"
    bl_label = "Row"
    layout_type = "row"

    def on_create(self, context):
        self.add_interface_input()
        self.add_interface_output()
        self.add_interface_output()
        self.add_string_input()

    def evaluate(self, context):
        self.code = f"""
                    # pass
                    row = {self.active_layout}.row()
                        # pass
                    {self.outputs[0].python_value}
                    {self.outputs[1].python_value}
                    """

    def draw_node(self, context, layout):
        pass