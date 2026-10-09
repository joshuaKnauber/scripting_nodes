from ....core import naming
from ....lib.code_format import literal_set
from ....lib.trees import node_by_id
from ....sockets.spec import Boolean, Interface, String
from ...base_node import ScriptingBaseNode
from .ops.panel_picker import (
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
    """A panel in any editor's sidebar, properties tab, ..."""

    bl_idname = "SNA_Node_Panel"
    bl_label = "Panel"
    sn_root = True
    sn_inputs = [
        String("label", "Label", default="Panel"),
        Boolean("visible", "Is Visible", default=True),
    ]
    sn_outputs = [Interface("header", "Header"), Interface("body", "Interface")]

    panel_space_type: bpy.props.EnumProperty(
        items=get_space_type_items,
        name="Space Type",
        description="Editor type where the panel appears",
    )
    panel_region_type: bpy.props.EnumProperty(
        items=get_region_type_items,
        name="Region Type",
        description="Region within the editor where the panel appears",
    )
    panel_context: bpy.props.EnumProperty(
        items=get_context_type_items,
        name="Context",
        description="Tab of the Properties editor (only used there)",
    )
    panel_category: bpy.props.StringProperty(
        name="Category",
        description="Sidebar tab name",
        default="Scripting Nodes",
    )
    panel_order: bpy.props.IntProperty(
        name="Order", description="Panel ordering index (higher values appear lower)"
    )
    option_default_closed: bpy.props.BoolProperty(
        name="Default Closed", description="Panel starts collapsed"
    )
    option_hide_header: bpy.props.BoolProperty(
        name="Hide Header", description="Hide the panel header"
    )

    def sn_names(self):
        return [naming.Class("class", "PT", naming.label(self))]

    def on_create(self):
        self.panel_space_type = "VIEW_3D"
        self.panel_region_type = "UI"
        self.panel_context = "NONE"

    def draw(self, context, layout):
        if is_picker_active() and get_active_picker_node_id() == self.id:
            layout.operator("sna.panel_picker_cancel", text="Cancel Picker", icon="X")
            layout.label(text="Click 'Pick This Location'", icon="INFO")
            layout.label(text="in any editor area")
            return
        row = layout.row(align=True)
        row.operator(
            "sna.panel_picker_start", text="", icon="EYEDROPPER"
        ).node_id = self.id
        op = row.operator(
            "sna.panel_node_settings", text="Settings", icon="PREFERENCES"
        )
        op.node_id = self.id

    def emit(self, ctx):
        options = set()
        if self.option_default_closed:
            options.add("DEFAULT_CLOSED")
        if self.option_hide_header:
            options.add("HIDE_HEADER")
        attrs = [
            f"bl_label = {ctx.input('label')}",
            f"bl_space_type = {self.panel_space_type!r}",
            f"bl_region_type = {self.panel_region_type!r}",
            f"bl_order = {self.panel_order}",
            f"bl_options = {literal_set(options)}" if options else "bl_options = set()",
        ]
        if self.panel_space_type == "PROPERTIES" and self.panel_context != "NONE":
            attrs.append(f"bl_context = {self.panel_context!r}")
        if self.panel_region_type == "UI" and self.panel_category:
            attrs.append(f"bl_category = {self.panel_category!r}")
        header = ""
        if ctx.is_linked("header"):
            header = f"""
                def draw_header(self, context):
                    {ctx.flow("header", layout="self.layout")}
            """

        ctx.module(f"""
            class {ctx.name("class")}(bpy.types.Panel):
                {ctx.join(attrs)}

                @classmethod
                def poll(cls, context):
                    return {ctx.input("visible")}

                {ctx.join([header])}

                def draw(self, context):
                    {ctx.flow("body", layout="self.layout")}
        """)
