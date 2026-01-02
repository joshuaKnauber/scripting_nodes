from .....lib.utils.code.format import indent
from ...base_node import ScriptingBaseNode
import bpy


class SNA_Node_Separator(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_Separator"
    bl_label = "Separator"

    def update_line(self, context):
        self._generate()

    line: bpy.props.BoolProperty(name="Show Line", default=False, update=update_line)

    def draw(self, context, layout):
        layout.prop(self, "line", text="Show Line")

    def on_create(self):
        self.add_input("ScriptingInterfaceSocket")
        inp = self.add_input("ScriptingFloatSocket", "Factor")
        inp.value = 1
        self.add_output("ScriptingInterfaceSocket")

    def generate(self):
        self.code = f"""
            {self.inputs[0].get_layout()}.separator(factor={self.inputs["Factor"].eval()}, type="{"LINE" if self.line else "SPACE"}")
            {indent(self.outputs[0].eval(), 3)}
        """
