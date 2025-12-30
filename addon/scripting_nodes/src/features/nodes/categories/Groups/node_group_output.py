"""
Group Output Node - Defines what the group returns.

This node:
1. Creates inputs for each output defined in the node tree interface
2. Generates return statements with the connected values
3. For INTERFACE type: typically doesn't return (or returns None)
4. For LOGIC type: returns data values
"""

from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
from scripting_nodes.src.features.nodes.categories.Groups.group_utils import (
    FLOW_SOCKET_TYPES,
    get_group_type,
    get_socket_idname,
)
import bpy


class SNA_Node_GroupOutput(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_GroupOutput"
    bl_label = "Group Output"

    # Store return statement separately from code to prevent duplicates
    return_code: str = ""

    @classmethod
    def poll(cls, ntree):
        """Only allow in group trees."""
        return ntree.bl_idname == "ScriptingNodeTree" and getattr(
            ntree, "is_group", False
        )

    def on_create(self):
        self._sync_sockets()

    def generate(self):
        if not self.node_tree.is_group:
            self.code = ""
            self.return_code = ""
            return

        # Ensure sockets are synced with interface before generating
        self._sync_sockets()

        is_interface = get_group_type(self.node_tree) == "INTERFACE"

        # Input sockets: index 0 = flow socket, index 1+ = data output values
        # For Interface functions, the layout is passed through the flow socket only.
        # Additional outputs should only be data types (Boolean, String, Integer, etc.)
        return_values = []

        # For Interface functions, ALWAYS return the flow socket's layout first
        # This carries the layout through the function call
        if is_interface and len(self.inputs) > 0:
            flow_socket = self.inputs[0]
            if hasattr(flow_socket, "get_layout"):
                layout_value = flow_socket.get_layout()
                return_values.append(layout_value)

        # Then add any explicit OUTPUT items from the interface (data sockets only)
        input_idx = 1  # Start after flow socket
        for item in self.node_tree.interface.items_tree:
            if hasattr(item, "in_out") and item.in_out == "OUTPUT":
                socket_idname = get_socket_idname(item.bl_socket_idname)
                # Skip flow socket types - they're handled by the flow socket above
                if socket_idname in FLOW_SOCKET_TYPES:
                    continue
                if input_idx < len(self.inputs):
                    socket = self.inputs[input_idx]
                    # Only data sockets should be used for additional outputs
                    return_values.append(socket.eval("None"))
                else:
                    return_values.append("None")
                input_idx += 1

        # Store return statement separately - don't use self.code
        # This prevents the return from being included multiple times
        # when multiple Interface sockets connect to this node
        self.code = ""  # Empty so eval() doesn't return the return statement

        if len(return_values) == 0:
            self.return_code = ""
        elif len(return_values) == 1:
            self.return_code = f"return {return_values[0]}"
        else:
            self.return_code = f"return ({', '.join(return_values)})"

    def on_group_socket_change(self, tree):
        """Called when the node tree's interface sockets change."""
        if tree != self.node_tree:
            return
        self._sync_sockets()
        self._generate()

    def _sync_sockets(self):
        """Sync node sockets with the node tree's interface.

        Intelligently updates sockets to preserve links where possible.
        """
        if not self.node_tree.is_group:
            return

        is_interface = get_group_type(self.node_tree) == "INTERFACE"

        # Determine what sockets we need
        flow_socket_type = (
            "ScriptingInterfaceSocket" if is_interface else "ScriptingLogicSocket"
        )
        flow_socket_name = "Interface" if is_interface else "Logic"

        needed_sockets = [(flow_socket_type, flow_socket_name)]

        for item in self.node_tree.interface.items_tree:
            if hasattr(item, "in_out") and item.in_out == "OUTPUT":
                socket_idname = get_socket_idname(item.bl_socket_idname)
                # Skip flow socket types - they can't be outputs
                if socket_idname in FLOW_SOCKET_TYPES:
                    continue
                needed_sockets.append((socket_idname, item.name))

        # Check if current sockets match needed sockets
        current_sockets = [(s.bl_idname, s.name) for s in self.inputs]

        if current_sockets == needed_sockets:
            # Sockets match, no changes needed
            return

        # Sync sockets intelligently
        self._sync_input_sockets(needed_sockets, is_interface)

    def _sync_input_sockets(self, needed_sockets, is_interface):
        """Sync input sockets with needed sockets, preserving links where possible.

        This method surgically updates only the sockets that need to change,
        keeping other sockets and their links intact.
        """
        current_count = len(self.inputs)
        needed_count = len(needed_sockets)

        # Process each position
        for i, (socket_type, socket_name) in enumerate(needed_sockets):
            if i < current_count:
                # Socket exists at this position - check if it needs updating
                existing = self.inputs[i]
                if existing.bl_idname == socket_type and existing.name == socket_name:
                    # Socket matches, nothing to do
                    continue

                # Socket needs to be replaced - store link info first
                link_info = []
                if existing.is_linked:
                    for link in existing.links:
                        from_socket_idx = list(link.from_node.outputs).index(
                            link.from_socket
                        )
                        link_info.append((link.from_node, from_socket_idx))

                # Remove old socket
                self.inputs.remove(existing)

                # Add new socket at this position
                new_socket = self.add_input(socket_type, socket_name)
                # Move it to the correct position
                if len(self.inputs) > 1:
                    self.inputs.move(len(self.inputs) - 1, i)

                # Restore links
                for from_node, from_socket_idx in link_info:
                    try:
                        if from_socket_idx < len(from_node.outputs):
                            from_socket = from_node.outputs[from_socket_idx]
                            self.node_tree.links.new(from_socket, self.inputs[i])
                    except Exception:
                        pass
            else:
                # Need to add a new socket
                self.add_input(socket_type, socket_name)

        # Remove any extra sockets at the end
        while len(self.inputs) > needed_count:
            self.inputs.remove(self.inputs[needed_count])
