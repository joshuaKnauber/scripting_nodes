"""
Patches for Blender's node tree interface menus to:
1. Safely handle interface.active being None
2. Filter out flow socket types (Interface, Program, Logic) from the add socket menu
   for function trees - only data sockets should be selectable
"""

import bpy
from scripting_nodes.src.lib.editor.editor import in_sn_tree


# Store references to original functions
_original_new_item_menu_draw = None
_original_context_menu_draw = None

# Socket types that should NOT appear in the interface add menu
FLOW_SOCKET_TYPES = {
    "ScriptingInterfaceSocket",
    "ScriptingProgramSocket",
    "ScriptingLogicSocket",
}

# Valid socket types for group interfaces (data sockets only)
SOCKET_TYPE_ITEMS = [
    ("ScriptingDataSocket", "Data", "Generic data"),
    ("ScriptingBlendDataSocket", "Blend Data", "Blend data (Scene, Object, etc.)"),
    ("ScriptingStringSocket", "String", "Text value"),
    ("ScriptingBooleanSocket", "Boolean", "True/False value"),
    ("ScriptingFloatSocket", "Float", "Decimal number"),
    ("ScriptingIntegerSocket", "Integer", "Whole number"),
    ("ScriptingVectorSocket", "Vector", "3D vector"),
    ("ScriptingColorSocket", "Color", "RGBA color"),
]


class SNA_OT_AddInterfaceSocket(bpy.types.Operator):
    """Add a new socket to the node group interface"""

    bl_idname = "sna.add_interface_socket"
    bl_label = "Add Interface Socket"
    bl_options = {"REGISTER", "UNDO"}

    item_type: bpy.props.EnumProperty(
        name="Item Type",
        items=[
            ("INPUT", "Input", "Add an input socket"),
            ("OUTPUT", "Output", "Add an output socket"),
            ("PANEL", "Panel", "Add a panel"),
        ],
        default="INPUT",
    )

    socket_type: bpy.props.EnumProperty(
        name="Socket Type", items=SOCKET_TYPE_ITEMS, default="ScriptingDataSocket"
    )

    @classmethod
    def poll(cls, context):
        return is_sn_group_tree(context)

    def execute(self, context):
        snode = context.space_data
        tree = snode.edit_tree
        interface = tree.interface

        if self.item_type == "PANEL":
            new_item = interface.new_panel(name="Panel")
        else:
            new_item = interface.new_socket(
                name=_get_socket_type_label(self.socket_type),
                in_out=self.item_type,
                socket_type=self.socket_type,
            )

        # Set as active
        interface.active = new_item

        # Mark tree as dirty
        tree.is_dirty = True

        return {"FINISHED"}


def is_sn_group_tree(context):
    """Check if we're editing a ScriptingNodeTree that is a group."""
    if not in_sn_tree(context):
        return False
    snode = context.space_data
    if snode and snode.edit_tree:
        tree = snode.edit_tree
        return getattr(tree, "is_group", False)
    return False


def is_sn_tree(context):
    """Check if we're editing any ScriptingNodeTree."""
    return in_sn_tree(context)


def _safe_menu_draw(original_draw, self, context):
    """Wrapper that safely handles interface.active being None."""
    try:
        snode = context.space_data
        if snode and snode.edit_tree:
            tree = snode.edit_tree
            if hasattr(tree, "interface"):
                active_item = tree.interface.active
                if active_item is None:
                    # Skip drawing the parts that need active_item
                    # Just show basic options
                    layout = self.layout
                    layout.label(text="No item selected", icon="INFO")
                    return
        # Call original draw
        if original_draw:
            original_draw(self, context)
    except Exception:
        # Fallback - just don't crash
        pass


def _get_socket_type_label(socket_idname):
    """Get human-readable label for a socket type."""
    for st in SOCKET_TYPE_ITEMS:
        if st[0] == socket_idname:
            return st[1]
    # Fallback - extract from idname
    if socket_idname.startswith("Scripting"):
        return socket_idname.replace("Scripting", "").replace("Socket", "")
    return socket_idname


def patched_new_item_menu_draw(self, context):
    """Patched draw for NODE_MT_node_tree_interface_new_item.

    For Scripting Node trees, shows simple Input/Output options that
    default to Data socket type.
    """
    layout = self.layout

    # Check if we're in a Scripting Node tree
    if is_sn_tree(context):
        # Simple menu with just Input and Output options
        layout.operator_context = "INVOKE_DEFAULT"

        op = layout.operator("sna.add_interface_socket", text="Input")
        op.item_type = "INPUT"
        op.socket_type = "ScriptingDataSocket"

        op = layout.operator("sna.add_interface_socket", text="Output")
        op.item_type = "OUTPUT"
        op.socket_type = "ScriptingDataSocket"
    else:
        # Not a Scripting Node tree, use original draw
        _safe_menu_draw(_original_new_item_menu_draw, self, context)


# Valid socket type idnames for group interfaces
VALID_SOCKET_IDNAMES = {st[0] for st in SOCKET_TYPE_ITEMS}


def patched_context_menu_draw(self, context):
    """Patched draw for NODE_MT_node_tree_interface_context_menu."""
    _safe_menu_draw(_original_context_menu_draw, self, context)


# Store original panel draw
_original_interface_panel_draw = None


def patched_interface_panel_draw(self, context):
    """Patched draw for NODE_PT_node_tree_interface.

    For Scripting Node trees, shows a filtered socket type menu instead of the
    full socket_type property which includes flow socket types.
    """
    # Check if we're in a Scripting Node tree
    if is_sn_tree(context):
        layout = self.layout
        snode = context.space_data
        tree = snode.edit_tree
        interface = tree.interface

        layout.use_property_split = True
        layout.use_property_decorate = False

        # Interface items list (same as original)
        row = layout.row()
        row.template_node_tree_interface(interface)

        # Operator buttons
        ops_col = row.column(align=True)
        ops_col.menu("NODE_MT_node_tree_interface_new_item", icon="ADD", text="")
        ops_col.operator("node.interface_item_remove", icon="REMOVE", text="")
        ops_col.separator()
        ops_col.operator("node.interface_item_duplicate", icon="DUPLICATE", text="")
        ops_col.separator()
        ops_col.menu(
            "NODE_MT_node_tree_interface_context_menu", icon="DOWNARROW_HLT", text=""
        )

        # Active item properties - with filtered socket type
        active_item = interface.active
        if active_item is not None:
            layout.separator()

            if active_item.item_type == "PANEL":
                layout.prop(active_item, "name")
                layout.prop(active_item, "description")
                layout.prop(active_item, "default_closed", text="Closed by Default")
            else:
                # Socket item
                layout.prop(active_item, "name")

                # Custom socket type selector - only show valid data socket types
                # Check if current type is valid
                current_type = active_item.bl_socket_idname
                if current_type not in VALID_SOCKET_IDNAMES:
                    layout.label(text="Invalid socket type for functions", icon="ERROR")

                # Show menu to change socket type
                layout.operator_menu_enum(
                    "sna.change_interface_socket_type",
                    "socket_type",
                    text=_get_socket_type_label(current_type),
                    icon="NODE",
                )

                layout.prop(active_item, "description")

                if active_item.item_type == "INPUT":
                    layout.prop(active_item, "hide_value")

                # Default value if applicable
                if hasattr(active_item, "default_value"):
                    layout.prop(active_item, "default_value")
    else:
        # Not a Scripting Node tree, use original draw
        if _original_interface_panel_draw:
            try:
                _original_interface_panel_draw(self, context)
            except Exception:
                pass


class SNA_OT_ChangeInterfaceSocketType(bpy.types.Operator):
    """Change the socket type of the active interface item"""

    bl_idname = "sna.change_interface_socket_type"
    bl_label = "Change Socket Type"
    bl_options = {"REGISTER", "UNDO"}

    def get_socket_type_items(self, context):
        """Return socket type items dynamically to ensure proper filtering."""
        return SOCKET_TYPE_ITEMS

    socket_type: bpy.props.EnumProperty(name="Socket Type", items=get_socket_type_items)

    @classmethod
    def poll(cls, context):
        if not is_sn_tree(context):
            return False
        snode = context.space_data
        if snode and snode.edit_tree:
            interface = snode.edit_tree.interface
            active = interface.active
            return active is not None and active.item_type != "PANEL"
        return False

    def execute(self, context):
        snode = context.space_data
        tree = snode.edit_tree
        interface = tree.interface
        active_item = interface.active

        if active_item and active_item.item_type != "PANEL":
            # Change the socket type by creating a new item and copying properties
            # Unfortunately Blender's API doesn't allow direct socket_type change
            # We need to remove and re-add with the new type
            item_type = active_item.item_type  # 'INPUT' or 'OUTPUT'
            name = active_item.name
            description = active_item.description

            # Get position in interface
            # Find index in items_tree
            idx = None
            for i, item in enumerate(interface.items_tree):
                if item == active_item:
                    idx = i
                    break

            # Remove old item
            interface.remove(active_item)

            # Add new item with correct type
            new_item = interface.new_socket(
                name=name,
                description=description,
                in_out=item_type,
                socket_type=self.socket_type,
            )

            # Move to original position if possible
            if idx is not None and idx < len(interface.items_tree):
                interface.move(new_item, idx)

            # Set as active
            interface.active = new_item

            # Mark tree as dirty
            tree.is_dirty = True

        return {"FINISHED"}


def register():
    global _original_new_item_menu_draw
    global _original_context_menu_draw
    global _original_interface_panel_draw

    # Monkey-patch the menus that crash when interface.active is None
    # and filter socket types for function trees
    try:
        new_item_menu = getattr(bpy.types, "NODE_MT_node_tree_interface_new_item", None)
        if new_item_menu is not None:
            _original_new_item_menu_draw = new_item_menu.draw
            new_item_menu.draw = patched_new_item_menu_draw
    except Exception:
        pass

    try:
        context_menu = getattr(
            bpy.types, "NODE_MT_node_tree_interface_context_menu", None
        )
        if context_menu is not None:
            _original_context_menu_draw = context_menu.draw
            context_menu.draw = patched_context_menu_draw
    except Exception:
        pass

    # Patch the interface panel to show filtered socket types for function trees
    try:
        panel_cls = getattr(bpy.types, "NODE_PT_node_tree_interface", None)
        if panel_cls is not None:
            _original_interface_panel_draw = panel_cls.draw
            panel_cls.draw = patched_interface_panel_draw
    except Exception:
        pass


def unregister():
    global _original_new_item_menu_draw
    global _original_context_menu_draw
    global _original_interface_panel_draw

    # Restore original menu draw functions
    try:
        if _original_new_item_menu_draw is not None:
            new_item_menu = getattr(
                bpy.types, "NODE_MT_node_tree_interface_new_item", None
            )
            if new_item_menu is not None:
                new_item_menu.draw = _original_new_item_menu_draw
            _original_new_item_menu_draw = None
    except Exception:
        pass

    try:
        if _original_context_menu_draw is not None:
            context_menu = getattr(
                bpy.types, "NODE_MT_node_tree_interface_context_menu", None
            )
            if context_menu is not None:
                context_menu.draw = _original_context_menu_draw
            _original_context_menu_draw = None
    except Exception:
        pass

    # Restore original panel draw
    try:
        if _original_interface_panel_draw is not None:
            panel_cls = getattr(bpy.types, "NODE_PT_node_tree_interface", None)
            if panel_cls is not None:
                panel_cls.draw = _original_interface_panel_draw
            _original_interface_panel_draw = None
    except Exception:
        pass
