from scripting_nodes.src.lib.utils.code.format import indent
from scripting_nodes.src.lib.utils.node_tree.scripting_node_trees import node_by_id
from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
from scripting_nodes.src.features.nodes.categories.Interface._operators.panel_picker import (
    is_picker_active,
    get_active_picker_node_id,
    get_space_type_items,
    get_region_type_items,
    get_context_type_items,
)
import bpy


class SNA_OT_PanelNodeSettings(bpy.types.Operator):
    bl_idname = "sna.panel_node_settings"
    bl_label = "Panel Settings"
    bl_description = "Configure panel settings"
    bl_options = {"REGISTER", "INTERNAL"}

    node_id: bpy.props.StringProperty()
    show_location: bpy.props.BoolProperty(default=False)

    def draw(self, context):
        layout = self.layout
        node = node_by_id(self.node_id)
        if not node:
            layout.label(text="Node not found")
            return

        # Options section
        col = layout.column(align=True)
        col.prop(node, "option_default_closed", toggle=True)
        col.prop(node, "option_hide_header", toggle=True)

        layout.separator()

        # Order
        row = layout.row(align=True)
        row.label(text="Order")
        row.prop(node, "panel_order", text="")

        layout.separator()

        # Show category for sidebar panels
        if node.panel_region_type == "UI":
            row = layout.row(align=True)
            row.label(text="Tab")
            row.prop(node, "panel_category", text="")
            layout.separator()

        # Location toggle section
        box = layout.box()
        row = box.row()
        row.prop(
            self,
            "show_location",
            text="Location",
            icon="TRIA_DOWN" if self.show_location else "TRIA_RIGHT",
            emboss=False,
        )

        if self.show_location:
            col = box.column(align=True)
            col.prop(node, "panel_space_type", text="")
            col.prop(node, "panel_region_type", text="")

            # Show context only for Properties editor
            if node.panel_space_type == "PROPERTIES":
                col.prop(node, "panel_context", text="")

    def execute(self, context):
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=200)


class SNA_Node_Panel(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_Panel"
    bl_label = "Panel"
    sn_options = {"ROOT_NODE"}

    # -- Properties --

    def update_props(self, context):
        self._generate()

    panel_space_type: bpy.props.EnumProperty(
        items=get_space_type_items,
        name="Space Type",
        description="Editor type where the panel appears",
        update=update_props,
    )

    panel_region_type: bpy.props.EnumProperty(
        items=get_region_type_items,
        name="Region Type",
        description="Region within the editor where the panel appears",
        update=update_props,
    )

    panel_context: bpy.props.EnumProperty(
        items=get_context_type_items,
        name="Context",
        description="Tab context for the Properties editor (only used when space is PROPERTIES)",
        update=update_props,
    )

    panel_category: bpy.props.StringProperty(
        name="Category",
        description="Tab name for sidebar panels (e.g. 'Tool', 'Edit')",
        default="Scripting Nodes",
        update=update_props,
    )

    panel_order: bpy.props.IntProperty(
        name="Order",
        description="Panel ordering index (higher values appear lower)",
        default=0,
        update=update_props,
    )

    # Panel options
    option_default_closed: bpy.props.BoolProperty(
        name="Default Closed",
        description="Panel starts collapsed by default",
        default=False,
        update=update_props,
    )

    option_hide_header: bpy.props.BoolProperty(
        name="Hide Header",
        description="Hide the panel header (makes panel non-collapsible)",
        default=False,
        update=update_props,
    )

    def on_create(self):
        # Inputs
        self.add_input("ScriptingStringSocket", "Label").value = "Panel"
        self.add_input("ScriptingBooleanSocket", "Is Visible").value = True

        # Outputs - interface hooks
        self.add_output("ScriptingInterfaceSocket", "Header")
        self.add_output("ScriptingInterfaceSocket", "Interface")

    def draw(self, context, layout):
        # Check if picker is active for this node
        if is_picker_active() and get_active_picker_node_id() == self.id:
            # Show cancel button when picker is active (no alert)
            layout.operator("sna.panel_picker_cancel", text="Cancel Picker", icon="X")
            layout.label(text="Click 'Pick This Location'", icon="INFO")
            layout.label(text="in any editor area")
            return

        # Picker and settings buttons
        row = layout.row(align=True)
        picker_op = row.operator("sna.panel_picker_start", text="", icon="EYEDROPPER")
        picker_op.node_id = self.id
        settings_op = row.operator(
            "sna.panel_node_settings", text="Settings", icon="PREFERENCES"
        )
        settings_op.node_id = self.id

    def generate(self):
        # Safety check: ensure inputs exist before generating
        if "Label" not in self.inputs or "Is Visible" not in self.inputs:
            return

        # Build bl_options set
        options = []
        if self.option_default_closed:
            options.append("'DEFAULT_CLOSED'")
        if self.option_hide_header:
            options.append("'HIDE_HEADER'")
        options_str = "{" + ", ".join(options) + "}" if options else "set()"

        # Build class attributes list
        class_attrs = [
            f'bl_idname = "SNA_PT_Panel_{self.id}"',
            f"bl_label = {self.inputs['Label'].eval()}",
            f"bl_space_type = '{self.panel_space_type}'",
            f"bl_region_type = '{self.panel_region_type}'",
        ]

        # Add context (only for PROPERTIES space)
        if self.panel_space_type == "PROPERTIES" and self.panel_context != "NONE":
            class_attrs.append(f'bl_context = "{self.panel_context}"')

        # Add category (for sidebar panels)
        if self.panel_region_type == "UI" and self.panel_category:
            class_attrs.append(f'bl_category = "{self.panel_category}"')

        # Add order and options
        class_attrs.append(f"bl_order = {self.panel_order}")
        class_attrs.append(f"bl_options = {options_str}")

        # Format class attributes
        attrs_code = "\n    ".join(class_attrs)

        # Set up header layout variable
        self.outputs["Header"].layout = f"header_{self.id}"

        # Build poll method
        poll_code = self.inputs["Is Visible"].eval("True")
        poll_method = f"""
    @classmethod
    def poll(cls, context):
        return {poll_code}
"""

        # Build draw_header method
        header_code = self.outputs["Header"].eval("pass")
        draw_header_method = f"""
    def draw_header(self, context):
        header_{self.id} = self.layout
        {indent(header_code, 2)}
"""

        self.code = f"""
import bpy

class SNA_PT_Panel_{self.id}(bpy.types.Panel):
    {attrs_code}
{poll_method}{draw_header_method}
    def draw(self, context):
        {indent(self.outputs["Interface"].eval("pass"), 2)}
        """
