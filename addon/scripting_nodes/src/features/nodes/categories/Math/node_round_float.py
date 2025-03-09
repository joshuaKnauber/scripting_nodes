from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
from scripting_nodes.src.lib.utils.sockets.modify import update_socket_type
import bpy


class SNA_Node_RoundFloat(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_RoundFloat"
    bl_label = "Round Float"

    round_up_or_down: bpy.props.EnumProperty(
        items=[
            ("UP", "Up", "Round up"),
            ("DOWN", "Down", "Round down"),
            ("NEAREST", "Nearest", "Round to the nearest float value"),
        ],
        name="Round",
        default="NEAREST",
        update=lambda self, context: self._generate(),
    )

    def draw(self, context, layout):
        layout.prop(self, "round_up_or_down", text="")

    def on_create(self):
        self.add_input("ScriptingFloatSocket", "Float")
        self.add_input("ScriptingIntegerSocket", "Decimals")
        self.add_output("ScriptingFloatSocket", "Rounded Float")

    def generate(self):
        value = self.inputs["Float"].eval()
        decimals = self.inputs["Decimals"].eval()

        if self.round_up_or_down == "UP":
            result = f"math.ceil({value} * (10 ** {decimals})) / (10 ** {decimals})"
        elif self.round_up_or_down == "DOWN":
            result = f"math.floor({value} * (10 ** {decimals})) / (10 ** {decimals})"
        elif self.round_up_or_down == "NEAREST":
            result = f"round({value}, {decimals})"

        if len(self.outputs) > 0:
            self.outputs[0].code = result
