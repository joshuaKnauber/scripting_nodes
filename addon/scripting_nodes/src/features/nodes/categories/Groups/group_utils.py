"""
Shared utilities for Group nodes.

This module contains common constants and helper functions used by
GroupInput, GroupOutput, and Group nodes.
"""

import re


# Flow socket types that should NOT be used for interface inputs/outputs.
# Only data sockets (Boolean, String, Integer, etc.) are valid.
FLOW_SOCKET_TYPES = frozenset(
    {
        "ScriptingInterfaceSocket",
        "ScriptingProgramSocket",
        "ScriptingLogicSocket",
        "NodeSocketVirtual",  # Blender's default when adding new sockets
    }
)

# Mapping from Blender interface socket types to our custom socket types.
# Includes both Blender native types and our custom types (since interfaces may use either).
INTERFACE_SOCKET_MAP = {
    # Blender native socket types
    "NodeSocketBool": "ScriptingBooleanSocket",
    "NodeSocketInt": "ScriptingIntegerSocket",
    "NodeSocketFloat": "ScriptingFloatSocket",
    "NodeSocketString": "ScriptingStringSocket",
    "NodeSocketVector": "ScriptingVectorSocket",
    "NodeSocketColor": "ScriptingColorSocket",
    # Our custom socket types (pass through)
    "ScriptingBooleanSocket": "ScriptingBooleanSocket",
    "ScriptingIntegerSocket": "ScriptingIntegerSocket",
    "ScriptingFloatSocket": "ScriptingFloatSocket",
    "ScriptingStringSocket": "ScriptingStringSocket",
    "ScriptingVectorSocket": "ScriptingVectorSocket",
    "ScriptingColorSocket": "ScriptingColorSocket",
    "ScriptingDataSocket": "ScriptingDataSocket",
    "ScriptingProgramSocket": "ScriptingProgramSocket",
    "ScriptingInterfaceSocket": "ScriptingInterfaceSocket",
}


def get_socket_idname(interface_socket_type):
    """Convert Blender's interface socket type to our custom socket type."""
    return INTERFACE_SOCKET_MAP.get(interface_socket_type, "ScriptingDataSocket")


def socket_name_to_param(name):
    """Convert socket name to valid Python parameter name."""
    # Replace spaces and special chars with underscores, lowercase
    clean = re.sub(r"[^a-zA-Z0-9]", "_", name).lower()
    # Remove leading digits
    clean = re.sub(r"^[0-9]+", "", clean)
    return clean or "param"


def get_group_input_node(tree):
    """Find the GroupInput node in a tree.

    Returns:
        The GroupInput node or None if not found.
    """
    for node in tree.nodes:
        if node.bl_idname == "SNA_Node_GroupInput":
            return node
    return None


def get_group_type(tree):
    """Get the group type (INTERFACE or LOGIC) from a tree.

    Returns:
        "INTERFACE" or "LOGIC" based on the GroupInput node's setting.
    """
    input_node = get_group_input_node(tree)
    if input_node:
        return getattr(input_node, "group_type", "LOGIC")
    return "LOGIC"


def is_interface_group(tree):
    """Check if a tree is an INTERFACE type group."""
    return get_group_type(tree) == "INTERFACE"


def is_flow_socket_type(socket_idname):
    """Check if a socket type is a flow socket (not a data socket)."""
    return socket_idname in FLOW_SOCKET_TYPES
