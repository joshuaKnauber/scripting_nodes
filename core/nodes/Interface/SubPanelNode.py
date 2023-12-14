import bpy

from ...utils.id import get_id

from ....constants import sockets

from ..base_node import SNA_BaseNode
from ..utils.references import NodePointer, node_search
from .PanelNode import SNA_NodePanel


class SNA_NodeSubpanel(SNA_BaseNode, bpy.types.Node):
    bl_idname = "SNA_NodeSubpanel"
    bl_label = "Subpanel"
    bl_width_default = 200

    panel: bpy.props.PointerProperty(
        type=NodePointer, name="Panel", description="Panel to be displayed"
    )
    blender_panel: bpy.props.StringProperty(
        name="Panel",
        update=lambda self, _: self.mark_dirty(),
    )
    blender_space: bpy.props.StringProperty(
        name="Space",
        update=lambda self, _: self.mark_dirty(),
    )
    blender_region: bpy.props.StringProperty(
        name="Region",
        update=lambda self, _: self.mark_dirty(),
    )
    blender_category: bpy.props.StringProperty(
        name="Category",
        update=lambda self, _: self.mark_dirty(),
    )
    blender_context: bpy.props.StringProperty(
        name="Context",
        update=lambda self, _: self.mark_dirty(),
    )

    origin: bpy.props.EnumProperty(
        name="Location",
        items=[
            ("PANEL", "Panel", "Add the subpanel to one of your panels"),
            (
                "SUBPANEL",
                "Subpanel",
                "Select one of your subpanels to create nested subpanels",
            ),
            (
                "BLENDER",
                "Blender Panel",
                "Add the subpanel to an existing panel within the blender interface",
            ),
        ],
        default="PANEL",
        description="Where to display the panel",
        update=lambda self, _: self.mark_dirty(),
    )

    default_closed: bpy.props.BoolProperty(
        default=False,
        name="Default Closed",
        description="Close the panel by default",
        update=lambda self, _: self.mark_dirty(),
    )
    hide_header: bpy.props.BoolProperty(
        default=False,
        name="Hide Header",
        description="Hide the header of the panel",
        update=lambda self, _: self.mark_dirty(),
    )
    expand_header: bpy.props.BoolProperty(
        default=False,
        name="Expand Header",
        description="Allow elements in the header to stretch across the whole layout",
        update=lambda self, _: self.mark_dirty(),
    )

    def update_title(self, context):
        self.name = self.title
        self.mark_dirty()

    title: bpy.props.StringProperty(
        default="Panel",
        name="Label",
        description="The label of the panel",
        update=update_title,
    )

    order: bpy.props.IntProperty(
        default=0,
        name="Order",
        description="The order index of the panel copared to your other panels",
        update=lambda self, _: self.mark_dirty(),
    )

    def draw_node(self, context: bpy.types.Context, layout: bpy.types.UILayout):
        row = layout.row()
        if self.origin == "PANEL":
            node_search(row, self.panel, SNA_NodePanel.bl_idname)
        elif self.origin == "SUBPANEL":
            node_search(row, self.panel, self.bl_idname)
        else:
            label = f"'{self.title}' ({self.blender_panel.replace('_', ' ').title()})"
            op = row.operator("sna.picker", text=label, icon="RESTRICT_SELECT_OFF")
            op.locations = "SUBPANELS"
            op.node = self.id
        row.operator(
            "sna.node_settings", text="", icon="PREFERENCES", emboss=False
        ).node = self.id

    def on_create(self):
        self.add_input(sockets.BOOLEAN, "Hide")
        out = self.add_output(sockets.INTERFACE, "Header")
        out.dynamic = True
        out = self.add_output(sockets.INTERFACE, "Interface")
        out.dynamic = True

    last_classname: bpy.props.StringProperty(default="")

    @property
    def space(self):
        if self.origin == "BLENDER":
            return self.blender_space
        return self.panel.node.space if self.panel.node else ""

    @property
    def region(self):
        if self.origin == "BLENDER":
            return self.blender_region
        return self.panel.node.region if self.panel.node else ""

    @property
    def category(self):
        if self.origin == "BLENDER":
            return self.blender_category
        return self.panel.node.category if self.panel.node else ""

    @property
    def context(self):
        if self.origin == "BLENDER":
            return self.blender_context
        return self.panel.node.context if self.panel.node else ""

    def generate(self, context, trigger):
        self.require_register = True
        panel_node = self.panel.node
        if (not panel_node or panel_node == self) and not self.origin == "BLENDER":
            return

        options = []
        if self.default_closed:
            options.append("'DEFAULT_CLOSED'")
        if self.hide_header:
            options.append("'HIDE_HEADER'")
        if self.expand_header:
            options.append("'HEADER_LAYOUT_EXPAND'")
        options = ", ".join(options)
        options = f"bl_options={{{options}}}" if options else ""

        panel_id = get_id()
        panel_classname = (
            f"SNA_PT_Subpanel_{panel_id}" if trigger == self else self.last_classname
        )
        self.last_classname = panel_classname

        parent = (
            panel_node.last_classname
            if self.origin != "BLENDER"
            else self.blender_panel
        )

        self.code = f"""
            class {panel_classname}(bpy.types.Panel):
                bl_idname = "{panel_classname}"
                bl_label = "{self.title}"
                bl_parent_id = "{parent}"
                bl_space_type = "{self.space}"
                bl_region_type = "{self.region}"
                {f'bl_category = "{self.category}"' if self.category else ""}
                {f'bl_context = "{self.context}"' if self.context else ""}
                bl_order = {self.order}
                {options}

                @classmethod
                def poll(cls, context):
                    return not ({self.inputs['Hide'].get_code()})

                def draw_header(self, context):
                    {self.outputs['Header'].get_code(5, "pass")}

                def draw(self, context):
                    {self.outputs['Interface'].get_code(5, "pass")}
        """

        self.outputs["Header"].set_meta("layout", "self.layout")
        self.outputs["Interface"].set_meta("layout", "self.layout")


def draw_settings(layout: bpy.types.UILayout, node: bpy.types.Node):
    layout.prop(node, "title")
    layout.separator()
    row = layout.row()
    row.prop(node, "default_closed")
    row.prop(node, "hide_header")
    row = layout.row()
    row.prop(node, "expand_header")
    row.prop(node, "order")
    layout.separator()
    layout.prop(node, "origin")
    if node.origin == "BLENDER":
        layout.separator()
        box = layout.box()
        box.prop(
            node,
            "expand_internals",
            text="Internal Settings",
            icon="TRIA_DOWN" if node.expand_internals else "TRIA_RIGHT",
            emboss=False,
        )
        if node.expand_internals:
            box.prop(node, "blender_panel")
            row = box.row()
            row.prop(node, "blender_space")
            row.prop(node, "blender_region")
            row = box.row()
            row.prop(node, "blender_category")
            row.prop(node, "blender_context")
