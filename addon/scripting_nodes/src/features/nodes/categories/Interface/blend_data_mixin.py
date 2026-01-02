"""
Mixin class for interface nodes that support both CUSTOM (property reference)
and BLENDER (direct blend data path) modes.
"""

import bpy

from .....lib.utils.blend_data.path_utils import format_name


class BlendDataModeMixin:
    """
    Mixin that adds BLENDER mode support to interface nodes.

    Nodes using this mixin should:
    1. Define the BLEND_DATA_MODE_PROPERTIES in their class body
    2. Call setup_blend_data_mode_properties() properties in their property definitions
    3. Use draw_mode_toggle() in their draw() method
    4. Use generate_prop_code() in their generate() method
    """

    @staticmethod
    def get_mode_items():
        return [
            ("CUSTOM", "Custom", "Use custom property reference"),
            ("BLENDER", "Blender", "Use Blender data path"),
        ]

    def update_mode(self, context):
        """Update socket visibility based on mode."""
        if len(self.inputs) > 1:
            data_socket = self.inputs.get("Data")
            if data_socket:
                if self.mode == "BLENDER":
                    data_socket.hide = (
                        self.blend_data_path != "" and not self.needs_data_input
                    )
                else:
                    data_socket.hide = False
        self._generate()

    def setup_from_path(self, path: str, prop_name: str, needs_input: bool):
        """Configure the node for BLENDER mode."""
        self.blend_data_path = path
        self.blend_prop_name = prop_name
        self.needs_data_input = needs_input

        # Update node label
        if prop_name:
            self.label = format_name(prop_name)
        else:
            self.label = ""

        # Update socket visibility
        data_socket = self.inputs.get("Data")
        if data_socket:
            data_socket.hide = not needs_input

        self._generate()

    def clear_blend_data_path(self):
        """Clear the blend data configuration."""
        self.blend_data_path = ""
        self.blend_prop_name = ""
        self.needs_data_input = False
        self.label = ""

        # Show the Data socket again
        data_socket = self.inputs.get("Data")
        if data_socket:
            data_socket.hide = False

        self._generate()

    def draw_mode_toggle(self, layout, context, prop_ref_attr: str = "prop"):
        """
        Draw the mode toggle row with appropriate content.

        Args:
            layout: The UILayout to draw into
            context: Blender context
            prop_ref_attr: The attribute name for the property reference (default "prop")

        Returns:
            True if in BLENDER mode with valid path, False otherwise
        """
        row = layout.row(align=True)

        if self.mode == "CUSTOM":
            row.prop_search(
                self, prop_ref_attr, context.scene.sna, "references", text=""
            )
            row.prop(self, "mode", icon="BLENDER", icon_only=True, text="")
            if not self.inputs["Data"].is_linked:
                layout.label(text="Connect data source", icon="INFO")
            return False
        else:  # BLENDER mode
            if self.blend_prop_name:
                display_name = format_name(self.blend_prop_name)
                row.label(text=display_name)
                op = row.operator("sna.blend_data_clear_path", text="", icon="X")
                op.node_name = self.name
            else:
                op = row.operator(
                    "sna.blend_data_paste_path", text="Paste Path", icon="PASTEDOWN"
                )
                op.node_name = self.name
            row.prop(self, "mode", icon="USER", icon_only=True, text="")

            if (
                self.blend_prop_name
                and self.needs_data_input
                and not self.inputs["Data"].is_linked
            ):
                layout.label(text="Connect data source", icon="INFO")

            return bool(self.blend_prop_name)

    def get_prop_data_and_name(self, prop_ref_attr: str = "prop"):
        """
        Get the data code and property name based on current mode.

        Args:
            prop_ref_attr: The attribute name for the property reference (default "prop")

        Returns:
            Tuple of (data_code, prop_name, error_message or None)
            If error_message is not None, generation should show that error.
        """
        if self.mode == "BLENDER":
            if not self.blend_prop_name:
                return None, None, None  # No configuration yet

            if self.needs_data_input:
                if not self.inputs["Data"].is_linked:
                    return None, None, "No data connected"
                data_code = self.inputs["Data"].eval()
            else:
                data_code = self.blend_data_path

            return data_code, self.blend_prop_name, None
        else:
            # CUSTOM mode
            ref = bpy.context.scene.sna.references.get(getattr(self, prop_ref_attr))
            if ref and ref.node:
                prop_name = getattr(ref.node, "prop_name", "")
                if prop_name:
                    if not self.inputs["Data"].is_linked:
                        return None, None, "No data connected"
                    data_code = self.inputs["Data"].eval()
                    return data_code, prop_name, None
            return None, None, None


# Property definitions to add to nodes using the mixin
# Nodes should include these in their class definition
def blend_data_mode_properties():
    """
    Returns a dict of properties to add to nodes using BlendDataModeMixin.
    Call this in the node class and unpack with **

    Note: Due to Blender's property system, these need to be defined directly
    on the class. Use _register_blend_data_mode_properties() instead.
    """
    return {
        "mode": bpy.props.EnumProperty(
            name="Mode",
            items=BlendDataModeMixin.get_mode_items(),
            default="CUSTOM",
            update=BlendDataModeMixin.update_mode,
        ),
        "blend_data_path": bpy.props.StringProperty(
            name="Blend Data Path",
            description="The full blend data path",
            default="",
        ),
        "blend_prop_name": bpy.props.StringProperty(
            name="Property Name",
            description="The property name (last segment)",
            default="",
        ),
        "needs_data_input": bpy.props.BoolProperty(
            name="Needs Data Input",
            description="Whether the Data input socket is needed",
            default=False,
        ),
    }
