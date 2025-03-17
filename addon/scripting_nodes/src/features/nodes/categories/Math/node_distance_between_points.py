from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
import bpy


class SNA_Node_DistanceBetweenPoints(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_DistanceBetweenPoints"
    bl_label = "Distance Between Points"

    def update_dimension(self, context):
        for socket in self.inputs:
            if hasattr(socket, "dimension"):
                socket.dimension = self.dimension
        self._generate()

    dimension: bpy.props.EnumProperty(
        name="Dimensions",
        description="Vector dimensions",
        items=[
            ("2", "Vec2", "Two-dimensional vectors"),
            ("3", "Vec3", "Three-dimensional vectors"),
            ("4", "Vec4", "Four-dimensional vectors (with w component)"),
        ],
        default="3",
        update=update_dimension,
    )

    def on_create(self):
        self.add_input("ScriptingVectorSocket", "Point A")
        self.add_input("ScriptingVectorSocket", "Point B")
        self.add_output("ScriptingFloatSocket", "Distance")

        for socket in self.inputs:
            if hasattr(socket, "dimension"):
                socket.dimension = self.dimension

    def draw(self, context, layout):
        if any(not socket.is_linked for socket in self.inputs):
            layout.prop(self, "dimension", text="")

    def generate(self):
        self.code_global = "import math"

        point_a = self.inputs["Point A"].eval()
        point_b = self.inputs["Point B"].eval()

        self.outputs["Distance"].code = (
            f"math.sqrt(sum((a - b)**2 for a, b in zip({point_a}, {point_b})))"
        )
