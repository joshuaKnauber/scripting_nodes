"""Script Function: calls a function of one of the add-on's scripts (Addon
Data › Scripts, core/scripts.py). The function's signature declares the
sockets (core/script_signatures.py): parameters are inputs, return values
outputs; `context`, `layout`, `self` and `event` get what the flow has, taking
`layout` makes it an interface node."""

import zlib

import bpy

from ....core import naming
from ....core import scripts as script_list
from ....core.context import NodeError
from ....sockets.spec import Flow
from ...base_node import ScriptingBaseNode
from ._script_nodes import current_specs

_items = []  # Blender needs the items of dynamic enums kept alive


def _value(name):
    """A stable enum value per function name: the picked function stays
    picked when functions are added or moved."""
    return zlib.crc32(name.encode()) & 0x7FFFFFFF or 1


def _function_items(self, context):
    names = self.functions()
    _items[:] = [
        (name, f"{name}()", f"Call {name}() of the script", _value(name))
        for name in names
    ]
    if self.function_name and self.function_name not in names:
        missing = f"{self.function_name}() (missing)"
        _items.append(("", missing, "The script doesn't define it anymore", 0))
    elif not names:
        _items.append(("", "No Functions", "The script defines no functions", 0))
    return _items


def _get_function(self):
    name = self.function_used()
    return _value(name) if name in self.functions() else 0


def _set_function(self, value):
    names = {_value(name): name for name in self.functions()}
    self.function_name = names.get(value, "")


def _get_script(self):
    script = script_list.find(self.script_id)
    return script_list.label(script) if script else ""


def _set_script(self, value):
    script = next((s for text, s in script_list.choices() if text == value), None)
    if value and script is None:
        return  # text that isn't a choice keeps the current one
    new_id = script.id if script else ""
    if new_id != self.script_id:
        self.script_id = new_id
        self.function_name = ""  # its run(), else its first function
    self.mark_dirty()


def _search_script(self, context, edit_text):
    return [text for text, _ in script_list.choices()]


class SNA_Node_ScriptFunction(ScriptingBaseNode, bpy.types.Node):
    """Call a function of one of the add-on's scripts: its parameters are the
    inputs, its return values the outputs."""

    bl_idname = "SNA_Node_ScriptFunction"
    bl_label = "Script Function"
    bl_width_default = 200

    script_id: bpy.props.StringProperty(options={"HIDDEN"})
    script: bpy.props.StringProperty(
        name="Script",
        description="Script of the add-on (in the Files list)",
        get=_get_script,
        set=_set_script,
        search=_search_script,
    )
    function_name: bpy.props.StringProperty(
        name="Function", description="Function of the script the node calls"
    )
    function: bpy.props.EnumProperty(
        name="Function",
        description="Function of the script the node calls",
        items=_function_items,
        get=_get_function,
        set=_set_function,
    )
    data_only: bpy.props.BoolProperty(
        name="Without Flow",
        description="No flow sockets: the function is called where its results "
        "are used (once per used result), e.g. to compute a value in a panel",
    )

    # -- the function -----------------------------------------------------------

    def script_item(self):
        """The picked script of the list, or None."""
        return script_list.find(self.script_id)

    def functions(self):
        script = self.script_item()
        return script.script_functions() if script is not None else []

    def function_used(self):
        """The picked function (even if the script lost it: the node shows
        that instead of calling another one), else `run()`, else the
        script's first one."""
        if self.function_name:
            return self.function_name
        names = self.functions()
        if "run" in names:
            return "run"
        return names[0] if names else ""

    def picked(self):
        """(name, Run) of the function the node calls."""
        item = self.script_item()
        if item is None:
            if self.script_id:
                raise NodeError("The script was removed from the add-on")
            raise NodeError("Pick a script")
        script = item.script()
        name = self.function_used()
        if not script.functions:
            raise NodeError(f"{script_list.label(item)} defines no functions")
        if name not in script.functions:
            raise NodeError(f"{script_list.label(item)} has no function {name}()")
        return name, script.functions[name]

    def is_data_only(self, run):
        return self.data_only and bool(run.outputs) and not run.draws

    # -- sockets ----------------------------------------------------------------

    def socket_specs(self):
        try:
            run = self.picked()[1]
        except NodeError:
            if self.script_item() is None:
                return [Flow()], [Flow("next")]
            return current_specs(self)  # keep the links while it's broken
        if self.is_data_only(run):
            return list(run.inputs), list(run.outputs)
        kind = "INTERFACE" if run.draws else "PROGRAM"
        return (
            [Flow(kind=kind), *run.inputs],
            [Flow("next", kind=kind), *run.outputs],
        )

    # -- code -------------------------------------------------------------------

    def sn_names(self):
        script = self.script_item()
        return script_list.names(script) if script is not None else []

    def emit(self, ctx):
        name, run = self.picked()
        script = self.script_item()
        alias = ctx.script("module", "alias", script.script_source(), script.folder)
        names = ctx.scope.names
        implicit = {
            "context": ctx.context,
            "layout": ctx.layout,
            "self": "self" if "self" in names else "None",
            "event": "event" if "event" in names else "None",
        }
        args = [
            f"{param}={implicit[param] if param in implicit else ctx.input(param)}"
            for param in run.params
        ]
        call = f"{alias}.{name}({', '.join(args)})"
        if self.is_data_only(run):
            if len(run.outputs) == 1:
                ctx.output(run.outputs[0].key, call)
            else:
                for i, spec in enumerate(run.outputs):
                    ctx.output(spec.key, f"{call}[{i}]")
            return
        if run.outputs:
            results = [ctx.var(naming.snake(s.label, "result")) for s in run.outputs]
            for spec, result in zip(run.outputs, results):
                ctx.output(spec.key, result)
            call = f"{', '.join(results)} = {call}"
        ctx.code(f"""
            {call}
            {ctx.flow("next")}
        """)

    # -- UI -------------------------------------------------------------------

    def draw_label(self):
        try:
            return f"{self.picked()[0]}()"
        except NodeError:
            return self.bl_label

    def draw(self, context, layout):
        row = layout.row(align=True)
        row.alert = bool(self.script_id) and self.script_item() is None
        row.prop(
            self, "script", text="", icon="FILE_SCRIPT", placeholder="Pick a script"
        )
        if self.script_item() is None:
            if not self.script_id:
                op = layout.operator("sna.new_script_for", icon="ADD")
                op.node_id = self.id
                layout.label(text="Or add one in the Files panel")
            return
        layout.prop(self, "function", text="")
        try:
            run = self.picked()[1]
        except NodeError:
            return
        if run.outputs and not run.draws:
            layout.prop(self, "data_only")
