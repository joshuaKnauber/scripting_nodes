import bpy

from ..base_socket import ScriptingBaseSocket

FLOW_KINDS = [
    ("PROGRAM", "Program", "Runs code"),
    ("LOGIC", "Logic", "Runs code (entry points like operators and events)"),
    ("INTERFACE", "Interface", "Draws UI into a layout"),
]

FLOW_COLORS = {
    "PROGRAM": (0.35, 0.35, 0.35, 1),
    "LOGIC": (1.0, 1.0, 1.0, 1),
    "INTERFACE": (0.95, 0.65, 0.0, 1),
}


class ScriptingFlowSocket(ScriptingBaseSocket):
    """Control flow between nodes. `kind` only changes the color and which
    sockets it connects to: Program and Logic both run code and connect to
    each other, Interface flows draw UI and only connect to Interface."""

    bl_idname = "ScriptingFlowSocket"
    bl_label = "Flow"
    socket_shape = "DIAMOND"

    kind: bpy.props.EnumProperty(items=FLOW_KINDS, default="PROGRAM")

    @property
    def socket_type(self):
        return "INTERFACE" if self.kind == "INTERFACE" else "EXEC"

    def draw_value(self, context, layout, text):
        layout.label(text=text)

    def draw_color(self, context, node):
        return FLOW_COLORS[self.kind]

    @classmethod
    def draw_color_simple(cls):
        return FLOW_COLORS["PROGRAM"]
