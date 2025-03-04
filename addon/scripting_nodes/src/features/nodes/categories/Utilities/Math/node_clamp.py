from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
from scripting_nodes.src.lib.utils.sockets.modify import update_socket_type
import bpy


class SNA_Node_Clamp(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_Clamp"
    bl_label = "Clamp"

    def update_data_type(self, context):
        self._generate()

    as_integer: bpy.props.BoolProperty(
        name="As Integer",
        description="Output the result as an integer",
        default=False,
        update=lambda self, context: self.update_output_socket(context),
    )

    def update_output_socket(self, context):
        if self.as_integer:
            if self.outputs[0].bl_idname != "ScriptingIntegerSocket":
                update_socket_type(self.outputs[0], "ScriptingIntegerSocket")
        else:
            if self.outputs[0].bl_idname != "ScriptingFloatSocket":
                update_socket_type(self.outputs[0], "ScriptingFloatSocket")
        self._generate()

    def on_create(self):
        self.add_input("ScriptingFloatSocket", "Value")
        self.add_input("ScriptingFloatSocket", "Min")
        self.add_input("ScriptingFloatSocket", "Max")
        self.add_output("ScriptingFloatSocket", "Result")

    def draw(self, context, layout):
        layout.prop(self, "as_integer", text="Integer Output")

    def generate(self):
        value = self.inputs["Value"].eval()
        min_val = self.inputs["Min"].eval()
        max_val = self.inputs["Max"].eval()

        if len(self.outputs) > 0:
            if self.as_integer:
                self.outputs[0].code = f"int(max({min_val}, min({max_val}, {value})))"
            else:
                self.outputs[0].code = f"max({min_val}, min({max_val}, {value}))"
