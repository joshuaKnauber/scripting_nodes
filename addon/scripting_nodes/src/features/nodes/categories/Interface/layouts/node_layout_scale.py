from scripting_nodes.src.lib.utils.code.format import indent
from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
import bpy


class SNA_Node_LayoutScale(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_LayoutScale"
    bl_label = "Set Layout Scale"

    def update_fixed_scale(self, context):
        self._generate()

    fixed_scale: bpy.props.BoolProperty(
        default=False, name="Fixed Scale", update=update_fixed_scale
    )

    def draw(self, context, layout):
        layout.prop(self, "fixed_scale")

    def on_create(self):
        self.add_input("ScriptingInterfaceSocket")
        inp = self.add_input("ScriptingFloatSocket", "Scale X")
        inp.value = 0
        inp = self.add_input("ScriptingFloatSocket", "Scale Y")
        inp.value = 0
        self.add_output("ScriptingInterfaceSocket")

    def generate(self):
        self.code = f"""
            {self.inputs[0].get_layout()}.{"ui_units_x" if self.fixed_scale else "scale_x"} = {self.inputs["Scale X"].eval()}
            {self.inputs[0].get_layout()}.{"ui_units_y" if self.fixed_scale else "scale_y"} = {self.inputs["Scale Y"].eval()}
            {indent(self.outputs[0].eval(), 3)}
        """
