import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_InterfaceScriptNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_InterfaceScriptNode"
    bl_label = "Interface Script"
    node_color = "INTERFACE"
    bl_width_default = 200

    def on_create(self, context):
        self.add_interface_input()
        self.add_string_input("Line")
        self.add_dynamic_string_input("Line")

    def evaluate(self, context):
        lines = [f"exec({inp.python_value})" for inp in self.inputs[1:-1]]
        self.code = f"""
                    {self.indent(lines, 5)}
                    """