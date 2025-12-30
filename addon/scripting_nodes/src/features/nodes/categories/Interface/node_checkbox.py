from scripting_nodes.src.lib.utils.code.format import indent
from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
import bpy


class SNA_Node_Checkbox(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_Checkbox"
    bl_label = "Checkbox"
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

    toggle: bpy.props.BoolProperty(
        name="Toggle",
        description="Display as a toggle button (-1 to use default)",
        default=False,
        update=update_prop,
    )

    invert_checkbox: bpy.props.BoolProperty(
        name="Invert",
        description="Draw checkbox value inverted",
        default=False,
        update=update_prop,
    )

    def draw(self, context, layout):
        layout.prop_search(self, "prop", context.scene.sna, "references", text="")
        row = layout.row(align=True)
        row.prop(self, "emboss", toggle=True)
        row.prop(self, "toggle", toggle=True)
        row.prop(self, "invert_checkbox", text="Invert", toggle=True)

    def on_create(self):
        self.add_input("ScriptingInterfaceSocket")
        self.add_input("ScriptingBlendDataSocket", "Data")
        self.add_input("ScriptingStringSocket", "Text")
        self.add_output("ScriptingInterfaceSocket")

    def on_ref_change(self, node):
        self._generate()

    def generate(self):
        ref = bpy.context.scene.sna.references.get(self.prop)
        if ref and ref.node:
            prop_name = getattr(ref.node, "prop_name", "")
            if prop_name:
                data_code = self.inputs["Data"].eval()
                text_code = self.inputs["Text"].eval()
                layout_code = self.inputs[0].get_layout()

                # Build prop arguments
                args = [f"data={data_code}", f'property="{prop_name}"']

                # Add text parameter
                args.append(f"text={text_code}")

                # Add emboss if not default
                if not self.emboss:
                    args.append("emboss=False")

                # Add toggle if enabled
                if self.toggle:
                    args.append("toggle=True")

                # Add invert_checkbox if enabled
                if self.invert_checkbox:
                    args.append("invert_checkbox=True")

                args_str = ", ".join(args)

                self.code = f"""
                    {layout_code}.prop({args_str})
                    {indent(self.outputs[0].eval(), 5)}
                """
            else:
                self.code = f"""
                    {indent(self.outputs[0].eval(), 5)}
                """
        else:
            self.code = f"""
                {indent(self.outputs[0].eval(), 4)}
            """
