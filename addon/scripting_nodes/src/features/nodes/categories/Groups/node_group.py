"""
Group Node - Calls a group defined in another node tree.

This node:
1. References a group node tree
2. Creates inputs for each group parameter (interface inputs)
3. Creates outputs for each group return value (interface outputs)
4. Generates the function call with proper arguments
5. For INTERFACE type: passes layout and chains to output
6. For LOGIC type: calls function with data arguments, provides return values
"""

from scripting_nodes.src.lib.utils.code.format import indent
from scripting_nodes.src.features.node_tree.node_tree import ScriptingNodeTree
from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
from scripting_nodes.src.features.nodes.categories.Groups.group_utils import (
    FLOW_SOCKET_TYPES,
    get_group_input_node,
    get_socket_idname,
    is_interface_group,
    socket_name_to_param,
)
import bpy


class SNA_Node_Group(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_Group"
    bl_label = "Group"

    def poll_tree(self, tree):
        """Only show group trees of the ScriptingNodeTree type."""
        return (
            tree.bl_idname == ScriptingNodeTree.bl_idname
            and getattr(tree, "is_group", False)
            and tree != self.node_tree  # Don't allow self-reference
        )

    def update_tree(self, context):
        self._sync_sockets()
        self._generate()

    group_tree: bpy.props.PointerProperty(
        name="Group",
        type=bpy.types.NodeTree,
        poll=poll_tree,
        update=update_tree,
    )

    def draw_buttons(self, context, layout):
        row = layout.row(align=True)
        row.template_ID(self, "group_tree")
        if not self.group_tree:
            op = row.operator("sna.add_group", text="Add", icon="ADD")
            op.node_id = self.id

    def generate(self):
        if not self.group_tree:
            return

        # Ensure sockets are synced with group interface before generating
        self._sync_sockets()

        func_name = self.group_tree.module_name
        is_interface = is_interface_group(self.group_tree)

        # Set output socket values (layout/code) FIRST before any eval calls
        # This ensures downstream nodes can get the correct layout
        self._setup_output_sockets()

        # Build the import statement
        if self.group_tree != self.node_tree:
            self.code_global = f"""
from .{self.group_tree.module_name} import {func_name}
"""
        else:
            self.code_global = ""

        # Build argument list
        args = []

        # For interface groups, pass the layout first
        if is_interface:
            # Get layout from input or use default (flow socket is at index 0)
            if len(self.inputs) > 0 and hasattr(self.inputs[0], "get_layout"):
                layout_var = self.inputs[0].get_layout()
            else:
                layout_var = "layout"
            args.append(layout_var)

        # Add data arguments from interface inputs
        # Input sockets: index 0 = flow socket, index 1+ = data inputs
        input_idx = 1  # Start after flow socket
        for item in self.group_tree.interface.items_tree:
            if hasattr(item, "in_out") and item.in_out == "INPUT":
                socket_idname = get_socket_idname(item.bl_socket_idname)
                # Skip flow socket types - only data sockets are valid inputs
                if socket_idname in FLOW_SOCKET_TYPES:
                    continue
                if input_idx < len(self.inputs):
                    socket = self.inputs[input_idx]
                    args.append(socket.eval())
                else:
                    args.append("None")
                input_idx += 1

        args_str = ", ".join(args)

        # Generate the call
        if is_interface:
            # Interface functions ALWAYS return the layout as the first value,
            # plus any additional OUTPUT items from the interface.
            # Return structure: (layout, output1, output2, ...) or just layout if no outputs
            # Output sockets: index 0 = Interface flow, index 1+ = data outputs
            output_items = []
            for item in self.group_tree.interface.items_tree:
                if hasattr(item, "in_out") and item.in_out == "OUTPUT":
                    socket_idname = get_socket_idname(item.bl_socket_idname)
                    # Skip flow socket types - only data sockets are valid outputs
                    if socket_idname in FLOW_SOCKET_TYPES:
                        continue
                    output_items.append(
                        (socket_name_to_param(item.name), item.bl_socket_idname)
                    )

            # Build variable names for all return values
            # First return value is always the layout (for Interface flow socket)
            layout_var = f"_fn_{self.id}_layout"

            if len(output_items) == 0:
                # Only layout is returned
                call_code = f"{layout_var} = {func_name}({args_str})"
            else:
                # Layout + additional outputs are returned as tuple
                output_var_names = [f"_fn_{self.id}_{name}" for name, _ in output_items]
                all_vars = [layout_var] + output_var_names
                call_code = f"{', '.join(all_vars)} = {func_name}({args_str})"

                # Set output socket values (index 1+ for data outputs)
                for i, (var_name, (_, socket_type)) in enumerate(
                    zip(output_var_names, output_items)
                ):
                    socket_idx = i + 1  # Skip the Interface flow socket at index 0
                    if socket_idx < len(self.outputs):
                        out_socket = self.outputs[socket_idx]
                        self._set_output_socket_value(out_socket, var_name, socket_type)

            # Set the layout on the Interface flow socket (index 0)
            if len(self.outputs) > 0 and hasattr(self.outputs[0], "layout"):
                self.outputs[0].layout = layout_var

            # Flow socket is always at index 0
            if len(self.outputs) > 0:
                output_socket = self.outputs[0]
                output_code = output_socket.eval("")
                if output_code:
                    self.code = f"""
{call_code}
{indent(output_code, 0)}
"""
                else:
                    self.code = call_code
            else:
                self.code = call_code
        else:
            # Logic functions may have return values
            # Output sockets: index 0 = Logic flow, index 1+ = data outputs
            output_items = []
            for item in self.group_tree.interface.items_tree:
                if hasattr(item, "in_out") and item.in_out == "OUTPUT":
                    socket_idname = get_socket_idname(item.bl_socket_idname)
                    # Skip flow socket types - only data sockets are valid outputs
                    if socket_idname in FLOW_SOCKET_TYPES:
                        continue
                    output_items.append(
                        (socket_name_to_param(item.name), item.bl_socket_idname)
                    )

            if len(output_items) == 0:
                # No return values
                call_code = f"{func_name}({args_str})"
            elif len(output_items) == 1:
                # Single return value - store in a variable
                var_name = f"_fn_{self.id}_{output_items[0][0]}"
                call_code = f"{var_name} = {func_name}({args_str})"
                # Output socket is at index 1 (after Logic flow socket)
                if len(self.outputs) > 1:
                    out_socket = self.outputs[1]
                    self._set_output_socket_value(
                        out_socket, var_name, output_items[0][1]
                    )
            else:
                # Multiple return values - unpack
                var_names = [f"_fn_{self.id}_{name}" for name, _ in output_items]
                call_code = f"{', '.join(var_names)} = {func_name}({args_str})"
                # Set output socket codes by index (starting at index 1)
                for i, (var_name, (_, socket_type)) in enumerate(
                    zip(var_names, output_items)
                ):
                    socket_idx = i + 1  # Skip the Logic flow socket at index 0
                    if socket_idx < len(self.outputs):
                        out_socket = self.outputs[socket_idx]
                        self._set_output_socket_value(out_socket, var_name, socket_type)

            # Add continuation - flow socket is always at index 0
            if len(self.outputs) > 0:
                logic_output = self.outputs[0]
                continuation = logic_output.eval("")
                if continuation:
                    self.code = f"""
{call_code}
{indent(continuation, 0)}
"""
                else:
                    self.code = call_code
            else:
                self.code = call_code

    def _set_output_socket_value(self, socket, var_name, interface_socket_type):
        """Set the appropriate property on an output socket for its value.

        For Interface sockets, we set the 'layout' property.
        For other sockets, we set the 'code' property.
        """
        # Check if this is an interface socket type
        socket_idname = get_socket_idname(interface_socket_type)
        if socket_idname == "ScriptingInterfaceSocket":
            if hasattr(socket, "layout"):
                socket.layout = var_name
        else:
            if hasattr(socket, "code"):
                socket.code = var_name

    def _setup_output_sockets(self):
        """Set layout/code properties on output sockets.

        Called at the start of generate() to ensure values are available
        before any downstream nodes call get_layout().
        Output sockets: index 0 = flow socket, index 1+ = data outputs
        """
        if not self.group_tree:
            return

        is_interface = is_interface_group(self.group_tree)

        # Count OUTPUT items (only data sockets, not flow socket types)
        output_items = []
        for item in self.group_tree.interface.items_tree:
            if hasattr(item, "in_out") and item.in_out == "OUTPUT":
                socket_idname = get_socket_idname(item.bl_socket_idname)
                if socket_idname in FLOW_SOCKET_TYPES:
                    continue
                output_items.append(item)

        # For Interface functions, ALWAYS set layout on flow socket (index 0)
        # Interface functions always return the layout as the first value
        if is_interface:
            if len(self.outputs) > 0:
                output_socket = self.outputs[0]
                if hasattr(output_socket, "layout"):
                    var_name = f"_fn_{self.id}_layout"
                    output_socket.layout = var_name

        # Set up explicit output sockets (index 1+)
        output_idx = 1  # Start after flow socket
        for item in output_items:
            if output_idx < len(self.outputs):
                var_name = f"_fn_{self.id}_{socket_name_to_param(item.name)}"
                self._set_output_socket_value(
                    self.outputs[output_idx], var_name, item.bl_socket_idname
                )
            output_idx += 1

    def on_group_socket_change(self, tree):
        """Called when the referenced function tree's interface changes."""
        if tree != self.group_tree:
            return
        self._sync_sockets()
        self._generate()

    def _sync_sockets(self):
        """Sync node sockets with the function tree's interface.

        Intelligently updates sockets to preserve links where possible.
        """
        if not self.group_tree:
            if len(self.inputs) > 0 or len(self.outputs) > 0:
                self.inputs.clear()
                self.outputs.clear()
            return

        is_interface = is_interface_group(self.group_tree)

        # Determine what sockets we need
        flow_socket_type = (
            "ScriptingInterfaceSocket" if is_interface else "ScriptingLogicSocket"
        )
        flow_socket_name = "Interface" if is_interface else "Logic"

        needed_inputs = [(flow_socket_type, flow_socket_name)]
        # needed_outputs stores (socket_idname, name, interface_socket_type) for data sockets
        # and (socket_idname, name) for the flow socket
        needed_outputs = [(flow_socket_type, flow_socket_name, None)]

        for item in self.group_tree.interface.items_tree:
            if hasattr(item, "in_out") and item.in_out == "INPUT":
                socket_idname = get_socket_idname(item.bl_socket_idname)
                # Skip flow socket types - they can't be inputs
                if socket_idname in FLOW_SOCKET_TYPES:
                    continue
                needed_inputs.append((socket_idname, item.name))
            elif hasattr(item, "in_out") and item.in_out == "OUTPUT":
                socket_idname = get_socket_idname(item.bl_socket_idname)
                # Skip flow socket types - they can't be outputs
                if socket_idname in FLOW_SOCKET_TYPES:
                    continue
                needed_outputs.append((socket_idname, item.name, item.bl_socket_idname))

        # Check if current sockets match needed sockets (compare just type and name)
        current_inputs = [(s.bl_idname, s.name) for s in self.inputs]
        current_outputs = [(s.bl_idname, s.name) for s in self.outputs]
        needed_inputs_cmp = [(t, n) for t, n in needed_inputs]
        needed_outputs_cmp = [(t, n) for t, n, *_ in needed_outputs]

        if (
            current_inputs == needed_inputs_cmp
            and current_outputs == needed_outputs_cmp
        ):
            # Sockets already match, but still need to set output socket values
            self._set_output_socket_values(needed_outputs)
            return

        # Sync inputs - update in place where possible
        self._sync_socket_list(
            self.inputs, needed_inputs, is_output=False, is_interface=is_interface
        )

        # Sync outputs - update in place where possible
        self._sync_socket_list(
            self.outputs,
            [(t, n) for t, n, *_ in needed_outputs],
            is_output=True,
            is_interface=is_interface,
        )

        # Set output socket values (layout/code) immediately so they're available for eval
        self._set_output_socket_values(needed_outputs)

    def _set_output_socket_values(self, needed_outputs):
        """Set layout/code properties on output sockets immediately.

        This ensures the values are available when downstream nodes call get_layout().
        Output sockets: index 0 = flow socket, index 1+ = data outputs
        """
        # Skip the flow socket at index 0, process data outputs starting at index 1
        for i, item in enumerate(needed_outputs[1:], start=1):
            if i < len(self.outputs):
                socket_idname, socket_name, interface_socket_type = item
                var_name = f"_fn_{self.id}_{socket_name_to_param(socket_name)}"
                self._set_output_socket_value(
                    self.outputs[i], var_name, interface_socket_type
                )

    def _sync_socket_list(
        self, socket_collection, needed_sockets, is_output, is_interface
    ):
        """Sync a socket collection (inputs or outputs) with needed sockets.

        Uses index-based matching to handle duplicate socket names properly.
        Preserves links where socket position and type match.
        """
        current_count = len(socket_collection)
        needed_count = len(needed_sockets)

        # Process each position
        for i, (socket_type, socket_name) in enumerate(needed_sockets):
            if i < current_count:
                # Socket exists at this position - check if it needs updating
                existing = socket_collection[i]
                if existing.bl_idname == socket_type and existing.name == socket_name:
                    # Socket matches, nothing to do (but ensure layout is set for Interface output)
                    if (
                        is_output
                        and socket_name == "Interface"
                        and hasattr(existing, "layout")
                    ):
                        existing.layout = ""
                    continue

                # Socket needs to be replaced - store link info first
                link_info = []
                if existing.is_linked:
                    for link in existing.links:
                        if is_output:
                            to_socket_idx = list(link.to_node.inputs).index(
                                link.to_socket
                            )
                            link_info.append((link.to_node, to_socket_idx))
                        else:
                            from_socket_idx = list(link.from_node.outputs).index(
                                link.from_socket
                            )
                            link_info.append((link.from_node, from_socket_idx))

                # Remove old socket
                socket_collection.remove(existing)

                # Add new socket at this position
                if is_output:
                    new_socket = self.add_output(socket_type, socket_name)
                    if socket_name == "Interface" and hasattr(new_socket, "layout"):
                        new_socket.layout = ""
                else:
                    new_socket = self.add_input(socket_type, socket_name)

                # Move it to the correct position
                if len(socket_collection) > 1:
                    socket_collection.move(len(socket_collection) - 1, i)

                # Restore links
                for other_node, other_socket_idx in link_info:
                    try:
                        if is_output:
                            if other_socket_idx < len(other_node.inputs):
                                other_socket = other_node.inputs[other_socket_idx]
                                self.node_tree.links.new(
                                    socket_collection[i], other_socket
                                )
                        else:
                            if other_socket_idx < len(other_node.outputs):
                                other_socket = other_node.outputs[other_socket_idx]
                                self.node_tree.links.new(
                                    other_socket, socket_collection[i]
                                )
                    except Exception:
                        pass
            else:
                # Need to add a new socket
                if is_output:
                    new_socket = self.add_output(socket_type, socket_name)
                    if socket_name == "Interface" and hasattr(new_socket, "layout"):
                        new_socket.layout = ""
                else:
                    new_socket = self.add_input(socket_type, socket_name)

        # Remove any extra sockets at the end
        while len(socket_collection) > needed_count:
            socket_collection.remove(socket_collection[needed_count])
