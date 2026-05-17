"""Call Group node: invokes a function (group tree) from another tree.

Subclasses bpy.types.NodeCustomGroup to inherit Tab-to-enter group navigation
and the `contains_tree` recursion check. Sockets are managed manually because
SN uses its own custom socket types instead of NodeTreeInterface.
"""
import bpy
from .....lib.utils.code.format import indent
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
    return (
        tree.bl_idname == "ScriptingNodeTree"
        and getattr(tree, "is_group", False)
    )


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

    # Tree-level dependency: smart reload uses this to know that callers
    # need to refresh when the group's file changes.
    sn_tree_reference_properties = {"node_tree"}

    def update_data_only(self, context):
        if self._sync_sockets():
            self._generate()

    data_only: bpy.props.BoolProperty(
        name="Data Only",
        description=(
            "Call as a data expression returning the group's outputs, with no "
            "program-flow sockets. Unchecked: the group runs as a statement "
            "inside a program-flow chain"
        ),
        default=False,
        update=update_data_only,
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
        """Return (group_input, group_output) inside the referenced tree."""
        if not self.node_tree:
            return None, None
        group_input = None
        group_output = None
        for node in self.node_tree.nodes:
            if node.bl_idname == "SNA_Node_GroupInput" and group_input is None:
                group_input = node
            elif node.bl_idname == "SNA_Node_GroupOutput" and group_output is None:
                group_output = node
        return group_input, group_output

    def _expected_sockets(self):
        """Compute (inputs, outputs) the node should currently have."""
        inputs = []
        outputs = []
        if not self.data_only:
            inputs.append(("ScriptingProgramSocket", PROGRAM_INPUT_LABEL))
            outputs.append(("ScriptingProgramSocket", PROGRAM_OUTPUT_LABEL))
        group_input, group_output = self._find_interface_nodes()
        if group_input:
            for item in group_input.get_items():
                inputs.append((item["type"], item["name"]))
        if group_output:
            for item in group_output.get_items():
                outputs.append((item["type"], item["name"]))
        return inputs, outputs

    def _sync_sockets(self):
        """Rebuild sockets to match the expected signature. Returns True if changed.

        Preserves existing connections by snapshotting links keyed on socket
        name, recreating the sockets, then reattaching links where the name
        survived in the new signature.
        """
        expected_in, expected_out = self._expected_sockets()
        current_in = [(s.bl_idname, s.name) for s in self.inputs]
        current_out = [(s.bl_idname, s.name) for s in self.outputs]
        if current_in == expected_in and current_out == expected_out:
            return False

        # Snapshot existing links by socket name. The remote socket refs (on
        # other nodes) stay valid through our own socket removal, so we can
        # use them to recreate the links after rebuild.
        saved_in_links = {
            s.name: [l.from_socket for l in s.links] for s in self.inputs if s.is_linked
        }
        saved_out_links = {
            s.name: [l.to_socket for l in s.links] for s in self.outputs if s.is_linked
        }

        # Blender's node socket collections don't support .clear() - it's a
        # silent no-op. Use .remove() per-socket to actually drop them.
        while len(self.inputs):
            self.inputs.remove(self.inputs[0])
        while len(self.outputs):
            self.outputs.remove(self.outputs[0])

        new_in_by_name = {}
        new_out_by_name = {}
        for sock_type, name in expected_in:
            new_in_by_name[name] = self.add_input(sock_type, name)
        for sock_type, name in expected_out:
            new_out_by_name[name] = self.add_output(sock_type, name)

        # Restore links where the socket name survived the rebuild. Links to
        # sockets whose name disappeared (renamed or removed) are dropped.
        ntree = self.id_data
        for name, from_sockets in saved_in_links.items():
            target = new_in_by_name.get(name)
            if target is None:
                continue
            for from_sock in from_sockets:
                try:
                    ntree.links.new(from_sock, target)
                except Exception:
                    pass
        for name, to_sockets in saved_out_links.items():
            source = new_out_by_name.get(name)
            if source is None:
                continue
            for to_sock in to_sockets:
                try:
                    ntree.links.new(source, to_sock)
                except Exception:
                    pass

        return True

    def on_create(self):
        # Initial layout: program-flow sockets only (no group selected yet)
        self._sync_sockets()

    def update(self):
        """Blender invokes this on graph changes. Re-sync only when needed.

        Handles the case where node_tree is reassigned via the UI - the diff
        check in _sync_sockets makes this a no-op when nothing changed.
        """
        if self._sync_sockets():
            self._generate()

    def draw(self, context, layout):
        # template_ID is the standard ID-block picker - more reliable than
        # layout.prop for PointerProperty(type=NodeTree). Includes a "New"
        # button that creates a new group via our SNA_OT_NewGroup operator.
        layout.template_ID(self, "node_tree", new="sna.new_group")
        layout.prop(self, "data_only")
        if self.node_tree and not getattr(self.node_tree, "is_group", False):
            box = layout.box()
            box.alert = True
            box.label(text="Target is not a group tree", icon="ERROR")

    def generate(self):
        """Emit the function call.

        PROGRAM mode: emits `(r1, r2) = func(args)` inline, then continues the
        chain via the program output.
        DATA mode: sets each output socket's .code to the call expression
        (indexed for multi-return), no inline emission.
        """
        # No valid group target - in PROGRAM mode just continue the chain.
        # We also bail when the assigned tree isn't a group (no function will
        # be generated for it) - emitting an import/call would produce broken
        # code on import. The UI shows a warning in draw().
        if not self.node_tree or not getattr(self.node_tree, "is_group", False):
            if not self.data_only and len(self.outputs) > 0:
                next_code = self.outputs[0].eval()
                self.code_inline = f"{indent(next_code, 3)}"
            return

        func_name = self.node_tree.module_name

        # Cross-tree import (skip if calling from inside the same tree -
        # nothing to import in that case)
        if self.node_tree is not self.id_data:
            self.code_imports = f"from .{func_name} import {func_name}"

        # Build argument list from data input sockets (skip the program input).
        # Always pass _locals=locals() so the group's body can resolve method-
        # scope names like self.layout, context, event, dummy.
        arg_start = 1 if not self.data_only else 0
        args = [s.eval() for s in list(self.inputs)[arg_start:]]
        args.append("_locals=locals()")
        call_expr = f"{func_name}(" + ", ".join(args) + ")"

        # Find how many return values the group declares
        _, group_output = self._find_interface_nodes()
        return_count = len(group_output.get_items()) if group_output else 0

        if not self.data_only:
            # outputs[0] = program; outputs[1:] = return values
            next_code = self.outputs[0].eval()
            if return_count == 0:
                stmt = call_expr
            elif return_count == 1:
                ret_var = f"_group_ret_{self.id}"
                if len(self.outputs) > 1:
                    self.outputs[1].code = ret_var
                stmt = f"{ret_var} = {call_expr}"
            else:
                ret_vars = [
                    f"_group_ret_{self.id}_{i}" for i in range(return_count)
                ]
                for i, name in enumerate(ret_vars):
                    if i + 1 < len(self.outputs):
                        self.outputs[i + 1].code = name
                stmt = f"({', '.join(ret_vars)}) = {call_expr}"
            self.code_inline = f"""
                {stmt}
                {indent(next_code, 4)}
            """
        else:
            # DATA mode - each output's code is an expression
            if return_count == 1 and len(self.outputs) > 0:
                self.outputs[0].code = call_expr
            elif return_count > 1:
                for i in range(return_count):
                    if i < len(self.outputs):
                        self.outputs[i].code = f"({call_expr})[{i}]"
