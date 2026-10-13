"""Temp Override node - runs a sub-flow in bpy.context.temp_override().

Use when an operator (or any code) needs a different context than the
current one, typically a specific viewport area/region. Only connected
inputs are passed; the rest stays as in the current context.
"""

import bpy

from ....blend_data.rna import blend_data_spec
from ....sockets.spec import Flow
from ...base_node import ScriptingBaseNode

# temp_override() keyword, input label, type, is collection
OVERRIDE_KEYS = [
    ("window", "Window", "Window", False),
    ("screen", "Screen", "Screen", False),
    ("area", "Area", "Area", False),
    ("region", "Region", "Region", False),
    ("active_object", "Active Object", "Object", False),
    ("selected_objects", "Selected Objects", "Object", True),
]


class SNA_Node_TempOverride(ScriptingBaseNode, bpy.types.Node):
    """Run code with a different context (window, area, active object, ...)."""

    bl_idname = "SNA_Node_TempOverride"
    bl_label = "Temp Override"
    sn_inputs = [Flow()] + [
        blend_data_spec(key, label, rna_type, collection)
        for key, label, rna_type, collection in OVERRIDE_KEYS
    ]
    sn_outputs = [Flow("during", "During"), Flow("next", "After")]

    def emit(self, ctx):
        kwargs = [
            f"{key}={ctx.input(key)}" for key, *_ in OVERRIDE_KEYS if ctx.is_linked(key)
        ]
        ctx.code(f"""
            with bpy.context.temp_override({", ".join(kwargs)}):
                {ctx.flow("during")}
            {ctx.flow("next")}
        """)
