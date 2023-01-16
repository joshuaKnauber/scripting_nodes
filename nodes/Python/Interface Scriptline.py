import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_InterfaceScriptlineNode(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_InterfaceScriptlineNode"
    bl_label = "Interface Scriptline"
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