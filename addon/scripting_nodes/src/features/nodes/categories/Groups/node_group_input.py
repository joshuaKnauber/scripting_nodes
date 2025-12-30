"""
Group Input Node - Defines the group and its parameters.

This node:
1. Marks the group entry point (ROOT_NODE)
2. Creates outputs for each input parameter defined in the node tree interface
3. Generates the function definition with proper parameters
4. For INTERFACE type: includes a 'layout' parameter for UI chaining
5. For LOGIC type: just generates the function with data parameters
"""

from scripting_nodes.src.lib.utils.code.format import indent
from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
from scripting_nodes.src.features.nodes.categories.Groups.group_utils import (
    FLOW_SOCKET_TYPES,
    get_socket_idname,
    socket_name_to_param,
)
import bpy


class SNA_Node_GroupInput(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_GroupInput"
    bl_label = "Group Input"
    sn_options = {"ROOT_NODE"}

    def update_group_type(self, context):
        self._sync_sockets()
        self._generate()
        # Also update GroupOutput node in this tree
        for node in self.node_tree.nodes:
            if node.bl_idname == "SNA_Node_GroupOutput":
                node._sync_sockets()
                node._generate()
        # Update any Group nodes that reference this tree
        for tree in bpy.data.node_groups:
            if tree.bl_idname != "ScriptingNodeTree":
                continue
            for node in tree.nodes:
                if node.bl_idname == "SNA_Node_Group":
                    if (
                        hasattr(node, "group_tree")
                        and node.group_tree == self.node_tree
                    ):
                        node._sync_sockets()
                        node._generate()

    group_type: bpy.props.EnumProperty(
        name="Type",
        items=[
            ("INTERFACE", "Interface", "Group for UI layout"),
            ("LOGIC", "Logic", "Group for logic flow"),
        ],
        default="LOGIC",
        update=update_group_type,
    )

    @classmethod
    def poll(cls, ntree):
        """Only allow in group trees."""
        return ntree.bl_idname == "ScriptingNodeTree" and getattr(
            ntree, "is_group", False
        )

    def draw_buttons(self, context, layout):
        layout.prop(self, "group_type", text="")

    def on_create(self):
        # Initial output depends on function type
        self._sync_sockets()

    def generate(self):
        if not self.node_tree.is_group:
            self.code = ""
            self.code_global = ""
            return

        # Ensure sockets are synced with interface before generating
        self._sync_sockets()

        func_name = self.node_tree.module_name
        is_interface = self.group_type == "INTERFACE"

        # Always import bpy for the function body
        self.code_global = "import bpy"

        # Build parameter list from interface inputs AND set output socket codes
        # Output sockets: index 0 = flow socket, index 1+ = data parameter outputs
        params = []
        output_idx = 1  # Start after flow socket

        for item in self.node_tree.interface.items_tree:
            if hasattr(item, "in_out") and item.in_out == "INPUT":
                socket_idname = get_socket_idname(item.bl_socket_idname)
                # Skip flow socket types - they're handled by the flow socket above
                if socket_idname in FLOW_SOCKET_TYPES:
                    continue
                param_name = socket_name_to_param(item.name)
                params.append(param_name)
                # Ensure output socket code is set to the parameter name
                if output_idx < len(self.outputs):
                    socket = self.outputs[output_idx]
                    if hasattr(socket, "code"):
                        socket.code = param_name
                output_idx += 1

        # For interface functions, add 'layout' as first parameter
        if is_interface:
            params.insert(0, "layout")

        params_str = ", ".join(params)

        # Generate the function body - this is where connected nodes go
        # The flow socket chain will naturally include all nodes up to GroupOutput
        # Flow socket is always at index 0
        if len(self.outputs) > 0:
            socket = self.outputs[0]
            body_code = socket.eval("pass")
        else:
            body_code = "pass"

        # Find GroupOutput and append its return statement
        # GroupOutput stores return in return_code (not code) to prevent duplicates
        func_output_code = ""
        for node in self.node_tree.nodes:
            if node.bl_idname == "SNA_Node_GroupOutput":
                node._generate()  # Ensure GroupOutput has generated its return_code
                func_output_code = getattr(node, "return_code", "")
                break

        # Ensure body_code is not empty - if it is, use 'pass' as placeholder
        if not body_code or not body_code.strip():
            body_code = "pass"

        if func_output_code:
            # Append return statement on a new line
            body_code = f"{body_code}\n{func_output_code}"

        # Build the function definition with proper indentation
        # indent() with keep_first=True keeps first line as-is and indents subsequent lines
        indented_body = indent(body_code, 1)
        self.code = f"def {func_name}({params_str}):\n    {indented_body}"

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

        is_interface = self.group_type == "INTERFACE"

        # Determine what sockets we need
        flow_socket_type = (
            "ScriptingInterfaceSocket" if is_interface else "ScriptingLogicSocket"
        )
        flow_socket_name = "Interface" if is_interface else "Logic"

        needed_sockets = [(flow_socket_type, flow_socket_name)]

        for item in self.node_tree.interface.items_tree:
            if hasattr(item, "in_out") and item.in_out == "INPUT":
                socket_idname = get_socket_idname(item.bl_socket_idname)
                # Skip flow socket types - they can't be inputs
                if socket_idname in FLOW_SOCKET_TYPES:
                    continue
                needed_sockets.append((socket_idname, item.name))

        # Check if current sockets match needed sockets
        current_sockets = [(s.bl_idname, s.name) for s in self.outputs]

        if current_sockets == needed_sockets:
            # Sockets match, just update the code values
            self._update_socket_codes()
            return

        # Sync sockets intelligently
        self._sync_output_sockets(needed_sockets, is_interface)

        # Update socket codes
        self._update_socket_codes()

    def _update_socket_codes(self):
        """Update the code property for all data output sockets.

        Uses index-based access to handle duplicate socket names properly.
        Output sockets: index 0 = flow socket, index 1+ = data parameter outputs
        """
        output_idx = 1  # Start after flow socket
        for item in self.node_tree.interface.items_tree:
            if hasattr(item, "in_out") and item.in_out == "INPUT":
                if output_idx < len(self.outputs):
                    socket = self.outputs[output_idx]
                    if hasattr(socket, "code"):
                        param_name = socket_name_to_param(item.name)
                        socket.code = param_name
                output_idx += 1

    def _sync_output_sockets(self, needed_sockets, is_interface):
        """Sync output sockets with needed sockets, preserving links where possible.

        Uses index-based matching to handle duplicate socket names properly.
        """
        current_count = len(self.outputs)
        needed_count = len(needed_sockets)

        # Process each position
        for i, (socket_type, socket_name) in enumerate(needed_sockets):
            if i < current_count:
                # Socket exists at this position - check if it needs updating
                existing = self.outputs[i]
                if existing.bl_idname == socket_type and existing.name == socket_name:
                    # Socket matches, nothing to do (but ensure layout is set for Interface)
                    if socket_name == "Interface" and hasattr(existing, "layout"):
                        existing.layout = "layout"
                    continue

                # Socket needs to be replaced - store link info first
                link_info = []
                if existing.is_linked:
                    for link in existing.links:
                        to_socket_idx = list(link.to_node.inputs).index(link.to_socket)
                        link_info.append((link.to_node, to_socket_idx))

                # Remove old socket
                self.outputs.remove(existing)

                # Add new socket at this position
                new_socket = self.add_output(socket_type, socket_name)
                if socket_name == "Interface" and hasattr(new_socket, "layout"):
                    new_socket.layout = "layout"
                # Move it to the correct position
                if len(self.outputs) > 1:
                    self.outputs.move(len(self.outputs) - 1, i)

                # Restore links
                for to_node, to_socket_idx in link_info:
                    try:
                        if to_socket_idx < len(to_node.inputs):
                            to_socket = to_node.inputs[to_socket_idx]
                            self.node_tree.links.new(self.outputs[i], to_socket)
                    except Exception:
                        pass
            else:
                # Need to add a new socket
                new_socket = self.add_output(socket_type, socket_name)
                if socket_name == "Interface" and hasattr(new_socket, "layout"):
                    new_socket.layout = "layout"

        # Remove any extra sockets at the end
        while len(self.outputs) > needed_count:
            self.outputs.remove(self.outputs[needed_count])
