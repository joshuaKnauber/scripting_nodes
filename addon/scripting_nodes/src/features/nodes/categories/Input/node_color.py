from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
import bpy


class SNA_Node_Color(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_Color"
    bl_label = "Color"

    def update_use_alpha(self, context):
        self.outputs[0].use_alpha = self.use_alpha
        self._generate()

    # Whether to include alpha channel
    use_alpha: bpy.props.BoolProperty(
        name="Use Alpha",
        description="Include alpha channel in color values",
        default=False,
        update=update_use_alpha,
    )

    # RGB value
    rgb_value: bpy.props.FloatVectorProperty(
        name="Color",
        subtype="COLOR",
        size=3,
        min=0.0,
        max=1.0,
        default=(1.0, 1.0, 1.0),
        update=lambda self, context: self._generate(),
    )

    # RGBA value
    rgba_value: bpy.props.FloatVectorProperty(
        name="Color",
        subtype="COLOR",
        size=4,
        min=0.0,
        max=1.0,
        default=(1.0, 1.0, 1.0, 1.0),
        update=lambda self, context: self._generate(),
    )

    def draw(self, context, layout):
        layout.prop(self, "use_alpha", text="Use Alpha")

        # Show the appropriate color property
        if self.use_alpha:
            layout.prop(self, "rgba_value", text="")
        else:
            layout.prop(self, "rgb_value", text="")

    def on_create(self):
        self.add_output("ScriptingColorSocket")
        if hasattr(self, "outputs") and len(self.outputs) > 0:
            self.outputs[0].use_alpha = self.use_alpha

    def generate(self):
        if len(self.outputs) > 0:
            if self.use_alpha:
                self.outputs[0].code = (
                    f"({self.rgba_value[0]}, {self.rgba_value[1]}, {self.rgba_value[2]}, {self.rgba_value[3]})"
                )
            else:
                self.outputs[0].code = (
                    f"({self.rgb_value[0]}, {self.rgb_value[1]}, {self.rgb_value[2]})"
                )
