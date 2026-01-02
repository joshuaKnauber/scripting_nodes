from .....lib.utils.code.format import indent
from ...base_node import ScriptingBaseNode
import bpy


class SNA_Node_NumberField(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_NumberField"
    bl_label = "Number Field"
    sn_reference_properties = {"prop"}

    def update_prop(self, context):
        self._generate()

    prop: bpy.props.StringProperty(name="Property", update=update_prop)

    emboss: bpy.props.BoolProperty(
        name="Emboss",
        description="Draw the button with an embossed look",
        default=True,
        update=update_prop,
    )

    slider: bpy.props.BoolProperty(
        name="Slider",
        description="Display the value as a slider",
        default=False,
        update=update_prop,
    )

    def draw(self, context, layout):
        layout.prop_search(self, "prop", context.scene.sna, "references", text="")
        if not self.inputs[1].is_linked:
            layout.label(text="Connect data source", icon="INFO")
        row = layout.row(align=True)
        row.prop(self, "emboss", toggle=True)
        row.prop(self, "slider", toggle=True)

    def on_create(self):
        self.add_input("ScriptingInterfaceSocket")
        self.add_input("ScriptingBlendDataSocket", "Data")
        self.add_input("ScriptingStringSocket", "Text")
        self.add_output("ScriptingInterfaceSocket")

    def on_ref_change(self, node):
        self._generate()

    def generate(self):
        layout_code = self.inputs[0].get_layout()
        output_code = self.outputs[0].eval()

        ref = bpy.context.scene.sna.references.get(self.prop)
        if not ref or not ref.node:
            self.code = f"""
                {indent(output_code, 4)}
            """
            return

        prop_name = getattr(ref.node, "prop_name", "")
        if not prop_name:
            self.code = f"""
                {indent(output_code, 4)}
            """
            return

        if not self.inputs["Data"].is_linked:
            self.code = f"""
                {layout_code}.label(text="No data connected", icon="ERROR")
                {indent(output_code, 4)}
            """
            return

        data_code = self.inputs["Data"].eval()
        text_code = self.inputs["Text"].eval()

        args = [f"data={data_code}", f'property="{prop_name}"']
        args.append(f"text={text_code}")

        if not self.emboss:
            args.append("emboss=False")

        if self.slider:
            args.append("slider=True")

        args_str = ", ".join(args)

        self.code = f"""
            {layout_code}.prop({args_str})
            {indent(output_code, 3)}
        """
