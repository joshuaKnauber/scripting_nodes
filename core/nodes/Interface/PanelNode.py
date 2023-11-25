import bpy

from ....constants import sockets
from ...utils.id import get_id
from ..base_node import SNA_BaseNode


class SNA_NodePanel(SNA_BaseNode, bpy.types.Node):
    bl_idname = "SNA_NodePanel"
    bl_label = "Panel"
    bl_width_default = 200

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
    space: bpy.props.StringProperty(
        default="VIEW_3D",
        name="Space",
        description="The space type of the panel",
        update=lambda self, _: self.mark_dirty(),
    )
    region: bpy.props.StringProperty(
        default="UI",
        name="Region",
        description="The region type of the panel",
        update=lambda self, _: self.mark_dirty(),
    )
    category: bpy.props.StringProperty(
        default="Scripting Nodes",
        name="Category",
        description="The category of the panel",
        update=lambda self, _: self.mark_dirty(),
    )
    context: bpy.props.StringProperty(
        default="",
        name="Context",
        description="The context of the panel",
        update=lambda self, _: self.mark_dirty(),
    )

    def on_create(self):
        self.add_input(sockets.BOOLEAN, "Hide")
        self.add_output(sockets.INTERFACE, "Header")
        self.add_output(sockets.INTERFACE, "Interface")

    def draw_node(self, context: bpy.types.Context, layout: bpy.types.UILayout):
        row = layout.row()
        row.scale_y = 1.5
        label = f"'{self.title}' ({self.space.replace('_', ' ').title()})"
        op = row.operator("sna.picker", text=label, icon="RESTRICT_SELECT_OFF")
        op.locations = "PANELS"
        op.node = self.id
        row.operator(
            "sna.node_settings", text="", icon="PREFERENCES", emboss=False
        ).node = self.id

    last_classname: bpy.props.StringProperty(default="")

    def generate(self, context):
        self.require_register = True

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
            f"SNA_PT_Panel_{panel_id}"
            if context["trigger"] == self
            else self.last_classname
        )
        self.last_classname = panel_classname

        self.code = f"""
            class {panel_classname}(bpy.types.Panel):
                bl_idname = "{panel_classname}"
                bl_label = "{self.title}"
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
