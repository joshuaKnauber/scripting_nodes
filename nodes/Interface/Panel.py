import bpy
from ..base_node import SN_ScriptingBaseNode
from ...utils import get_python_name



class SN_PanelNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_PanelNode"
    bl_label = "Panel"
    bl_width_default = 200
    layout_type = "layout"
    is_trigger = True
    node_color = "INTERFACE"

    def on_create(self, context):
        self.add_boolean_input("Hide")
        self.add_interface_output("Panel")
        self.add_dynamic_interface_output("Panel")
        self.add_interface_output("Header")
        self.add_dynamic_interface_output("Header")

    label: bpy.props.StringProperty(default="New Panel",
                                    name="Label",
                                    description="The label of your panel",
                                    update=SN_ScriptingBaseNode._evaluate)

    space: bpy.props.StringProperty(default="VIEW_3D",
                                    name="Space",
                                    description="The space your panel is in",
                                    update=SN_ScriptingBaseNode._evaluate)

    region: bpy.props.StringProperty(default="UI",
                                    name="Region",
                                    description="The region your panel is in",
                                    update=SN_ScriptingBaseNode._evaluate)

    context: bpy.props.StringProperty(default="",
                                    name="Context",
                                    description="The context your panel is in",
                                    update=SN_ScriptingBaseNode._evaluate)

    category: bpy.props.StringProperty(default="New Category",
                                    name="Category",
                                    description="The category your panel is in",
                                    update=SN_ScriptingBaseNode._evaluate)

    order: bpy.props.IntProperty(default=0, min=0,
                                name="Order",
                                description="The order of your panel compared to the other panels",
                                update=SN_ScriptingBaseNode._evaluate)

    hide_header: bpy.props.BoolProperty(default=False,
                                    name="Hide Header",
                                    description="Hide the panels header",
                                    update=SN_ScriptingBaseNode._evaluate)

    expand_header: bpy.props.BoolProperty(default=False,
                                    name="Expand Header",
                                    description="Expands the header to fill the full panel width",
                                    update=SN_ScriptingBaseNode._evaluate)

    default_closed: bpy.props.BoolProperty(default=False,
                                    name="Default Closed",
                                    description="Closes the panel by default",
                                    update=SN_ScriptingBaseNode._evaluate)

    show_advanced: bpy.props.BoolProperty(default=False,
                                    name="Advanced Options",
                                    description="Show advanced python options for positioning the panel")

    def evaluate(self, context):
        uid = self.uuid
        py_name = get_python_name(self.label)
        idname = f"SNA_PT_{py_name.upper() if py_name else 'Panel'}_{uid}"

        options = []
        if self.hide_header: options.append("'HIDE_HEADER'")
        if self.expand_header: options.append("'HEADER_LAYOUT_EXPAND'")
        if self.default_closed: options.append("'DEFAULT_CLOSED'")

        self.code = f"""
                    class {idname}(bpy.types.Panel):
                        bl_label = "{self.label}"
                        bl_idname = "{idname}"
                        bl_space_type = '{self.space}'
                        bl_region_type = '{self.region}'
                        {f"bl_context = '{self.context}'" if self.context else ""}
                        {f"bl_category = '{self.category}'" if self.category else ""}
                        bl_order = {self.order}
                        {f"bl_options = {{{', '.join(options)}}}" if options else ""}

                        @classmethod
                        def poll(cls, context):
                            return not {self.inputs["Hide"].python_value}
                        
                        def draw_header(self, context):
                            layout = self.layout
                            {self.indent([out.python_value for out in filter(lambda out: out.name=='Header' and not out.dynamic, self.outputs)], 7)}

                        def draw(self, context):
                            layout = self.layout
                            {self.indent([out.python_value for out in filter(lambda out: out.name=='Panel' and not out.dynamic, self.outputs)], 7)}
                    """

        self.code_unregister = f"bpy.utils.unregister_class({idname})"
        self.code_register = f"bpy.utils.register_class({idname})"

    def draw_node(self, context, layout):
        row = layout.row()
        row.scale_y = 1.5
        op = row.operator("sn.activate_panel_picker", text=f"{self.space.replace('_', ' ').title()} {self.region.replace('_', ' ').title()} {self.context.replace('_', ' ').title()}", icon="EYEDROPPER")
        op.node_tree = self.node_tree.name
        op.node = self.name

        layout.prop(self, "label")
        layout.prop(self, "category")

        layout.prop(self, "order")
        layout.prop(self, "hide_header")
        layout.prop(self, "expand_header")
        layout.prop(self, "default_closed")

        box = layout.box()
        box.prop(self, "show_advanced", icon="TRIA_DOWN" if self.show_advanced else "TRIA_RIGHT", emboss=False)
        if self.show_advanced:
            box.prop(self, "space")
            box.prop(self, "region")
            box.prop(self, "context")