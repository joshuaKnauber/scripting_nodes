import bpy

from ....sockets.spec import Boolean, Color, Float, Integer, Vector
from ...base_node import ScriptingBaseNode

TYPES = [
    ("FLOAT", "Float", "A decimal number between Min and Max"),
    ("INTEGER", "Integer", "A whole number between Min and Max (both included)"),
    ("BOOLEAN", "Boolean", "True with the given probability"),
    ("VECTOR", "Vector", "Each value between Min and Max"),
    ("COLOR", "Color", "A random color"),
]


class SNA_Node_RandomValue(ScriptingBaseNode, bpy.types.Node):
    """A random number, boolean, vector or color, new every time it's used."""

    bl_idname = "SNA_Node_RandomValue"
    bl_label = "Random Value"
    sn_header_props = ("data_type",)

    data_type: bpy.props.EnumProperty(name="Type", items=TYPES)

    def socket_specs(self):
        if self.data_type == "INTEGER":
            inputs = [Integer("min", "Min"), Integer("max", "Max", default=100)]
            return inputs, [Integer("value", "Value")]
        if self.data_type == "BOOLEAN":
            inputs = [Float("probability", "Probability", default=0.5)]
            return inputs, [Boolean("value", "Value")]
        if self.data_type == "COLOR":
            return [], [Color("value", "Color")]
        inputs = [Float("min", "Min"), Float("max", "Max", default=1.0)]
        if self.data_type == "VECTOR":
            return inputs, [Vector("value", "Vector")]
        return inputs, [Float("value", "Value")]

    def emit(self, ctx):
        ctx.imports("import random")
        if self.data_type == "INTEGER":
            value = f"random.randint({ctx.input('min')}, {ctx.input('max')})"
        elif self.data_type == "BOOLEAN":
            value = f"random.random() < {ctx.input('probability')}"
        elif self.data_type == "COLOR":
            value = "(random.random(), random.random(), random.random())"
        elif self.data_type == "VECTOR":
            uniform = f"random.uniform({ctx.input('min')}, {ctx.input('max')})"
            value = f"({uniform}, {uniform}, {uniform})"
        else:
            value = f"random.uniform({ctx.input('min')}, {ctx.input('max')})"
        ctx.output("value", value)
