"""Temp Override node - wraps a sub-chain in bpy.context.temp_override().

Use when an operator (or any code) needs to run in a different context than
the current one — typically targeting a specific viewport area/region. Only
the override-kwargs whose input sockets are linked are passed; unconnected
keys are left at the current context's defaults.
"""
from .....lib.utils.code.format import indent
from ...base_node import ScriptingBaseNode
import bpy


# Socket label -> temp_override() kwarg. Sockets in this order define the
# node's visible inputs after the Before program socket.
OVERRIDE_KEYS = [
    ("Window", "window"),
    ("Screen", "screen"),
    ("Area", "area"),
    ("Region", "region"),
    ("Active Object", "active_object"),
    ("Selected Objects", "selected_objects"),
]


class SNA_Node_TempOverride(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_TempOverride"
    bl_label = "Temp Override"

    def on_create(self):
        self.add_input("ScriptingLogicSocket")
        for label, _ in OVERRIDE_KEYS:
            self.add_input("ScriptingBlendDataSocket", label)
        self.add_output("ScriptingLogicSocket", "During")
        self.add_output("ScriptingLogicSocket", "After")

    def generate(self):
        parts = []
        for i, (_label, key) in enumerate(OVERRIDE_KEYS, start=1):
            socket = self.inputs[i]
            if socket.is_linked:
                parts.append(f"{key}={socket.eval()}")
        kwargs = ", ".join(parts)

        during = self.outputs[0].eval("pass")
        after = self.outputs[1].eval()

        self.code_inline = f"""
            with bpy.context.temp_override({kwargs}):
                {indent(during, 4)}
            {indent(after, 3)}
        """
