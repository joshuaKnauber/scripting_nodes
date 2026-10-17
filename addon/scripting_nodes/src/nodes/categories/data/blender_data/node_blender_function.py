"""Blender Function node: calls a function of Blender data
(`context.active_object.modifiers.new(name="Bevel", type='BEVEL')`). The path
leads to the data the function belongs to (nodes/_blend_path.py), the
function's parameters and results become sockets (blend_data/rna.py)."""

import bpy

from .....blend_data import rna
from .....core.context import NodeError
from .....sockets.spec import Flow
from ...._blend_path import BlendPathMixin
from ....base_node import ScriptingBaseNode


def _preset(label, root, path, function):
    return (label, {"path_root": root, "path": path, "function": function})


class SNA_Node_BlenderFunction(BlendPathMixin, ScriptingBaseNode, bpy.types.Node):
    """Call a function of Blender data: add a modifier, create an object,
    select an object, link it to a collection, ..."""

    bl_idname = "SNA_Node_BlenderFunction"
    bl_label = "Blender Function"
    bl_width_default = 260

    # the path browser lists functions and Use Path sets one
    sn_calls_functions = True
    sn_presets = [
        _preset("Add Modifier", "CONTEXT", "active_object.modifiers", "new"),
        _preset("New Object", "DATA", "objects", "new"),
        _preset("Link Object", "CONTEXT", "collection.objects", "link"),
        _preset("Select Object", "CONTEXT", "active_object", "select_set"),
    ]

    function: bpy.props.StringProperty(name="Function")

    def path_accepts(self, step):
        """The path leads to the data the function belongs to."""
        return step.known and bool(step.rna_type or step.collection)

    def rna_function(self):
        return rna.function(self.path_final(), self.function) if self.function else None

    def socket_specs(self):
        inputs = [Flow(), *self.path_input_specs()]
        outputs = [Flow("next")]
        function = self.rna_function()
        if function is not None:
            for parameter in rna.parameters(function):
                inputs.append(rna.parameter_spec(parameter, _key(parameter)))
            for result in rna.parameters(function, outputs=True):
                outputs.append(rna.parameter_spec(result, _key(result)))
        return inputs, outputs

    def path_text(self):
        text = super().path_text()
        if not self.function:
            return text if self.path else "Pick a Function"
        call = f"{self.function}()"
        return f"{text} › {call}" if self.path else call

    def draw_label(self):
        if not self.function:
            return self.bl_label
        owner = self.path_label()
        return f"{owner} › {self.function}()" if owner else f"{self.function}()"

    def draw(self, context, layout):
        self.draw_path(layout)

    def emit(self, ctx):
        if not self.function:
            raise NodeError("Pick a function")
        function = self.rna_function()
        if function is None:
            owner = rna.label(self.path_final())
            raise NodeError(f"{owner} has no function {self.function}()")
        args = [_argument(ctx, parameter) for parameter in rna.parameters(function)]
        call = f"{self.path_expression(ctx)}.{self.function}({ctx.args(*args)})"

        results = rna.parameters(function, outputs=True)
        names = [ctx.var(result.identifier) for result in results]
        for result, name in zip(results, names):
            ctx.output(_key(result), name)
        assign = f"{', '.join(names)} = " if names else ""
        ctx.code(f"""
            {assign}{call}
            {ctx.flow("next")}
        """)


def _key(parameter):
    return f"param_{parameter.identifier}"


def _argument(ctx, parameter):
    """`name=value` for a parameter, None to leave it at its default."""
    name, key = parameter.identifier, _key(parameter)
    if parameter.type in {"POINTER", "COLLECTION"}:
        if ctx.is_linked(key):
            return f"{name}={ctx.input(key)}"
        if not parameter.is_required:
            return None
        if getattr(parameter, "is_never_none", False):
            raise NodeError(f"Connect the {parameter.name or name}")
        return f"{name}=None"
    if parameter.is_required:
        return f"{name}={ctx.input(key)}"
    default = rna.parameter_default(parameter)
    socket = ctx.node.socket(key)
    value = getattr(socket, "value", None)
    if isinstance(default, tuple) and value is not None:
        value = tuple(value)
    if not socket.is_linked and value == default:
        return None
    return f"{name}={ctx.input(key)}"
