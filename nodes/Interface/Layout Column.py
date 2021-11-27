import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode



class SN_LayoutColumnNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_LayoutColumnNode"
    bl_label = "Column"
    layout_type = "column"

    def on_create(self, context):
        self.add_interface_input()
        self.add_interface_output()
        self.add_interface_output()
        self.add_string_input()
        self.node_tree.links.new(self.inputs[0], self.outputs[0])

    def evaluate(self, context):
        self.code = f"""
                        # pass
                        column = {self.active_layout}.column()
                            # pass
                        {self.outputs[0].python_value}
                        {self.outputs[1].python_value}
                    """

    def draw_node(self, context, layout):
        pass