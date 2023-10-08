import bpy

from ....constants import sockets
from ...utils.id import get_id
from ..base_node import SN_BaseNode


class SN_PanelNode(SN_BaseNode, bpy.types.Node):
    bl_idname = "SN_PanelNode"
    bl_label = "Panel"

    default_closed: bpy.props.BoolProperty(default=True, name="Default Closed", description="Close the panel by default", update=lambda self, _: self.mark_dirty())
    hide_header: bpy.props.BoolProperty(default=False, name="Hide Header", description="Hide the header of the panel", update=lambda self, _: self.mark_dirty())
    expand_header: bpy.props.BoolProperty(default=False, name="Expand Header", description="Allow elements in the header to stretch across the whole layout", update=lambda self, _: self.mark_dirty())

    label: bpy.props.StringProperty(default="Panel", name="Label", description="The label of the panel", update=lambda self, _: self.mark_dirty())

    order: bpy.props.IntProperty(default=0, name="Order", description="The order index of the panel copared to your other panels", update=lambda self, _: self.mark_dirty())

    def on_create(self):
        self.add_input(sockets.BOOLEAN, "Hide")
        self.add_output(sockets.INTERFACE, "Header")
        self.add_output(sockets.INTERFACE, "Interface")

    def draw_node(self, context: bpy.types.Context, layout: bpy.types.UILayout):
        row = layout.row()
        row.prop(self, "name", text="")
        row.operator("sn.node_settings", text="", icon="PREFERENCES", emboss=False).node = self.name

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
        panel_classname = f"SNA_PT_Panel_{panel_id}"

        self.code = f"""
            class {panel_classname}(bpy.types.Panel):
                bl_idname = "{panel_classname}"
                bl_label = "{self.label}"
                bl_space_type = "NODE_EDITOR"
                bl_region_type = "UI"
                bl_category = "Scripting Nodes"
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
