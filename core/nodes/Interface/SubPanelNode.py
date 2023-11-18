import bpy

from ...utils.id import get_id

from ....constants import sockets

from ..base_node import SNA_BaseNode
from ..utils.references import NodePointer, node_search
from .PanelNode import SNA_NodePanel


class SNA_NodeSubpanel(SNA_BaseNode, bpy.types.Node):
    bl_idname = "SNA_NodeSubpanel"
    bl_label = "Subpanel"

    panel: bpy.props.PointerProperty(
        type=NodePointer, name="Panel", description="Panel to be displayed"
    )

    nested: bpy.props.BoolProperty(
        default=False,
        name="Nested Subpanel",
        description="Lets you select a subpanel to display this subpanel in",
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
        if not self.nested:
            node_search(row, self.panel, SNA_NodePanel.bl_idname)
        else:
            node_search(row, self.panel, self.bl_idname)
        row.operator(
            "sna.node_settings", text="", icon="PREFERENCES", emboss=False
        ).node = self.name

    def on_create(self):
        self.add_input(sockets.BOOLEAN, "Hide")
        self.add_output(sockets.INTERFACE, "Header")
        self.add_output(sockets.INTERFACE, "Interface")

    last_classname: bpy.props.StringProperty(default="")

    @property
    def space(self):
        return self.panel.node.space if self.panel.node else ""

    @property
    def region(self):
        return self.panel.node.region if self.panel.node else ""

    @property
    def category(self):
        return self.panel.node.category if self.panel.node else ""

    @property
    def context(self):
        return self.panel.node.context if self.panel.node else ""

    def generate(self, context):
        self.require_register = True
        panel_node = self.panel.node
        if not panel_node or panel_node == self:
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
        panel_classname = f"SNA_PT_Subpanel_{panel_id}"
        self.last_classname = panel_classname

        self.code = f"""
            class {panel_classname}(bpy.types.Panel):
                bl_idname = "{panel_classname}"
                bl_label = "{self.title}"
                bl_parent_id = "{panel_node.last_classname}"
                bl_space_type = "{panel_node.space}"
                bl_region_type = "{panel_node.region}"
                {f'bl_category = "{panel_node.category}"' if panel_node.category else ""}
                {f'bl_context = "{panel_node.context}"' if panel_node.context else ""}
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
