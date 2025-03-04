from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
from scripting_nodes.src.lib.utils.sockets.modify import update_socket_type
import bpy


class SNA_Node_MapRange(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_MapRange"
    bl_label = "Map Range"

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
        self.add_input("ScriptingFloatSocket", "Old Min")
        self.add_input("ScriptingFloatSocket", "Old Max")
        self.add_input("ScriptingFloatSocket", "New Min")
        self.add_input("ScriptingFloatSocket", "New Max")
        self.add_output("ScriptingFloatSocket", "Result")

    def draw(self, context, layout):
        layout.prop(self, "as_integer", text="Integer Output")

    def generate(self):
        value = self.inputs["Value"].eval()
        old_min = self.inputs["Old Min"].eval()
        old_max = self.inputs["Old Max"].eval()
        new_min = self.inputs["New Min"].eval()
        new_max = self.inputs["New Max"].eval()

        if len(self.outputs) > 0:
            if self.as_integer:
                self.outputs[0].code = (
                    f"int(({value} - {old_min}) * ({new_max} - {new_min}) / ({old_max} - {old_min}) + {new_min})"
                )
            else:
                self.outputs[0].code = (
                    f"({value} - {old_min}) * ({new_max} - {new_min}) / ({old_max} - {old_min}) + {new_min}"
                )
