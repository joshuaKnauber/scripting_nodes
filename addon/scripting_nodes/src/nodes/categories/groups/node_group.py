"""Call Group node: invokes a function (group tree) from another tree.

Subclasses bpy.types.NodeCustomGroup to inherit Tab-to-enter group navigation
and the `contains_tree` recursion check. Sockets are managed manually because
SN uses its own custom socket types instead of NodeTreeInterface.
"""

import bpy

from ....core.context import NodeError
from ....sockets.spec import Flow
from ...base_node import ScriptingBaseNode


PROGRAM_INPUT_LABEL = "Run"
PROGRAM_OUTPUT_LABEL = "After"


def _poll_group_tree_target(self, tree):
    """Filter for the node_tree dropdown - only SN group trees.

    Blender's data picker uses PointerProperty.poll (not poll_instance) to
    decide which items appear in the list. poll_instance only validates
    explicit assignments, so without this filter the dropdown shows every
    ScriptingNodeTree (addon trees and groups alike).
    """
    return tree.bl_idname == "ScriptingNodeTree" and getattr(tree, "is_group", False)


class SNA_Node_Group(bpy.types.NodeCustomGroup, ScriptingBaseNode):
    bl_idname = "SNA_Node_Group"
    bl_label = "Group"

    # Override the inherited NodeCustomGroup.node_tree to add a dropdown
    # filter. Without poll, Blender's picker shows every NodeTree of the
    # matching type (incl. our addon trees) since it has no notion of our
    # custom is_group flag.
    node_tree: bpy.props.PointerProperty(
        type=bpy.types.NodeTree,
        poll=_poll_group_tree_target,
    )

    # the generated call imports the group's function from that tree
    sn_tree_reference_properties = {"node_tree"}

    data_only: bpy.props.BoolProperty(
        name="Data Only",
        description=(
            "Call as a data expression returning the group's outputs, with no "
            "program-flow sockets. Unchecked: the group runs as a statement "
            "inside a program-flow chain"
        ),
        default=False,
    )

    @classmethod
    def poll(cls, ntree):
        # Callable from any ScriptingNodeTree (addon trees and other groups)
        return ntree.bl_idname == "ScriptingNodeTree"

    def poll_instance(self, group_tree):
        """Validate node_tree assignment - only group trees, no recursion."""
        if not group_tree or group_tree.bl_idname != "ScriptingNodeTree":
            return False
        if not getattr(group_tree, "is_group", False):
            return False
        # Built-in recursion check from Blender: prevents the assigned tree
        # from (transitively) containing this node's tree
        if hasattr(group_tree, "contains_tree") and group_tree.contains_tree(
            self.id_data
        ):
            return False
        return True

    def _find_interface_nodes(self):
        """(group input, group output) inside the referenced tree."""
        group_input = group_output = None
        if self.node_tree:
            for node in self.node_tree.nodes:
                if node.bl_idname == "SNA_Node_GroupInput" and group_input is None:
                    group_input = node
                elif node.bl_idname == "SNA_Node_GroupOutput" and group_output is None:
                    group_output = node
        return group_input, group_output

    def socket_specs(self):
        group_input, group_output = self._find_interface_nodes()
        inputs = [] if self.data_only else [Flow("flow", PROGRAM_INPUT_LABEL)]
        outputs = [] if self.data_only else [Flow("next", PROGRAM_OUTPUT_LABEL)]
        if group_input:
            inputs += group_input.item_specs()
        if group_output:
            outputs += group_output.item_specs()
        return inputs, outputs

    def update(self):
        """Blender calls this when node_tree is reassigned from the UI."""
        self.mark_dirty()

    def draw(self, context, layout):
        layout.template_ID(self, "node_tree", new="sna.new_group")
        layout.prop(self, "data_only")
        if self.node_tree and not getattr(self.node_tree, "is_group", False):
            box = layout.box()
            box.alert = True
            box.label(text="Target is not a group tree", icon="ERROR")

    def emit(self, ctx):
        tree = self.node_tree
        if tree is None or not getattr(tree, "is_group", False):
            raise NodeError("Pick a group")
        group_input, group_output = self._find_interface_nodes()
        function = ctx.symbol(tree, tree.module_name)
        args = [
            ctx.input(key)
            for key in (group_input.parameter_keys() if group_input else [])
        ]
        # pass what the group body may use from the caller's scope
        for name in ("self", "context", "event"):
            if name in ctx.scope.names:
                args.append(f"{name}={name}")
        if ctx.scope.layout:
            args.append(f"layout={ctx.layout}")
        call = f"{function}({', '.join(args)})"

        returns = group_output.parameter_keys() if group_output else []
        if self.data_only:
            for i, key in enumerate(returns):
                ctx.output(key, call if len(returns) == 1 else f"{call}[{i}]")
            return
        if not returns:
            statement = call
        else:
            names = [ctx.var("result") for _ in returns]
            for key, name in zip(returns, names):
                ctx.output(key, name)
            statement = f"{', '.join(names)} = {call}"
        ctx.code(f"""
            {statement}
            {ctx.flow("next")}
        """)
