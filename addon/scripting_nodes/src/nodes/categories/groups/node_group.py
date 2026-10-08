"""Group node: calls a function (a tree with a group interface).

Subclasses NodeCustomGroup for `node_tree` and Tab-to-enter. Blender doesn't
create sockets for custom group nodes, so they're declared from the tree's
interface like any other node's (keys are the interface item identifiers).
How the function is called depends on its interface, see core/functions.py.
"""

import bpy

from ....core import functions
from ....core.context import NodeError
from ....sockets.interface import SETTINGS
from ....sockets.spec import Socket
from ...base_node import ScriptingBaseNode


def _poll_function(self, tree):
    """Trees offered in the picker: functions that don't contain this one."""
    return (
        tree.bl_idname == "ScriptingNodeTree"
        and tree != self.id_data
        and functions.is_function(tree)
        and not functions.calls(tree, self.id_data)
    )


def _spec(item):
    attrs = {name: getattr(item, name) for name in SETTINGS if hasattr(item, name)}
    kind = attrs.pop("kind", None)
    default = getattr(item, "default_value", None)
    if default is not None and not isinstance(default, (str, bool, int, float)):
        default = tuple(default)
    spec = Socket(item.bl_socket_idname, item.identifier, item.name)
    if kind:
        spec.kind = kind
    if default is not None:
        spec.default = default
    spec.attrs.update(attrs)
    return spec


class SNA_Node_Group(bpy.types.NodeCustomGroup, ScriptingBaseNode):
    bl_idname = "SNA_Node_Group"
    bl_label = "Group"
    bl_width_default = 180

    # replaces NodeCustomGroup.node_tree to filter the picker
    node_tree: bpy.props.PointerProperty(
        type=bpy.types.NodeTree, name="Function", poll=_poll_function
    )

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == "ScriptingNodeTree"

    def poll_instance(self, tree):
        return tree is not None and _poll_function(self, tree)

    def socket_specs(self):
        tree = self.node_tree
        if tree is None:
            return [], []
        return (
            [_spec(item) for item in functions.sockets(tree, "INPUT")],
            [_spec(item) for item in functions.sockets(tree, "OUTPUT")],
        )

    def update(self):
        """Blender calls this when node_tree is set from the UI."""
        self.mark_dirty()

    def draw_label(self):
        return self.node_tree.name if self.node_tree else self.bl_label

    def draw(self, context, layout):
        layout.template_ID(self, "node_tree", new="sna.new_group")

    def emit(self, ctx):
        tree = self.node_tree
        if tree is None or not functions.is_function(tree):
            raise NodeError("Pick a function")
        problem = functions.problem(tree)
        if problem:
            raise NodeError(problem)

        args = [ctx.input(item.identifier) for item, _ in functions.parameters(tree)]
        # pass what the function body may use from the caller's scope
        for name in ("self", "context", "event"):
            if name in ctx.scope.names:
                args.append(f"{name}={name}")
        flow_input = functions.flow_input(tree)
        if flow_input is not None and flow_input.kind == "INTERFACE":
            args.append(f"layout={ctx.layout}")
        call = f"{ctx.symbol(tree, tree.module_name)}({', '.join(args)})"
        returns = [item.identifier for item in functions.returns(tree)]

        if flow_input is None:
            # pure function: an expression
            for i, key in enumerate(returns):
                ctx.output(key, call if len(returns) == 1 else f"{call}[{i}]")
            return

        if returns:
            names = [ctx.var("result") for _ in returns]
            for key, name in zip(returns, names):
                ctx.output(key, name)
            call = f"{', '.join(names)} = {call}"
        flow_output = functions.flow_output(tree)
        ctx.code(f"""
            {call}
            {ctx.flow(flow_output.identifier) if flow_output else ""}
        """)
