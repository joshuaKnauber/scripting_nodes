from scripting_nodes.src.lib.utils.code.format import indent
from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
from scripting_nodes.src.features.nodes.categories.Interface.blend_data_mixin import (
    BlendDataModeMixin,
)
import bpy


class SNA_Node_TextField(BlendDataModeMixin, ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_TextField"
    bl_label = "Text Field"
    sn_reference_properties = {"prop"}

    def update_prop(self, context):
        self._generate()

    # Mode properties from mixin
    mode: bpy.props.EnumProperty(
        name="Mode",
        items=BlendDataModeMixin.get_mode_items(),
        default="CUSTOM",
        update=BlendDataModeMixin.update_mode,
    )

    blend_data_path: bpy.props.StringProperty(
        name="Blend Data Path",
        description="The full blend data path",
        default="",
    )

    blend_prop_name: bpy.props.StringProperty(
        name="Property Name",
        description="The property name (last segment)",
        default="",
    )

    needs_data_input: bpy.props.BoolProperty(
        name="Needs Data Input",
        description="Whether the Data input socket is needed",
        default=False,
    )

    # Node-specific properties
    prop: bpy.props.StringProperty(name="Property", update=update_prop)

    emboss: bpy.props.BoolProperty(
        name="Emboss",
        description="Draw the button with an embossed look",
        default=True,
        update=update_prop,
    )

    def draw(self, context, layout):
        self.draw_mode_toggle(layout, context)
        layout.prop(self, "emboss")

    def on_create(self):
        self.add_input("ScriptingInterfaceSocket")
        self.add_input("ScriptingBlendDataSocket", "Data")
        self.add_input("ScriptingStringSocket", "Text")
        self.add_output("ScriptingInterfaceSocket")

    def on_ref_change(self, node):
        self._generate()

    def generate(self):
        layout_code = self.inputs[0].get_layout()

        data_code, prop_name, error = self.get_prop_data_and_name()

        if error:
            self.code = f"""
                {layout_code}.label(text="{error}", icon="ERROR")
                {indent(self.outputs[0].eval(), 5)}
            """
            return

        if not prop_name:
            # No configuration yet
            self.code = f"""
                {indent(self.outputs[0].eval(), 4)}
            """
            return

        text_code = self.inputs["Text"].eval()

        args = [f"data={data_code}", f'property="{prop_name}"']
        args.append(f"text={text_code}")

        if not self.emboss:
            args.append("emboss=False")

        args_str = ", ".join(args)

        self.code = f"""
            {layout_code}.prop({args_str})
            {indent(self.outputs[0].eval(), 4)}
        """
