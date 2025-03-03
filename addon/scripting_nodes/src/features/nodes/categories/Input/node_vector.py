from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
import bpy


class SNA_Node_Vector(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_Vector"
    bl_label = "Vector"

    def update_value(self, context):
        self._generate()

    def update_dimensions(self, context):
        # Update the socket dimension to match the node dimension
        if hasattr(self, "outputs") and len(self.outputs) > 0:
            self.outputs[0].dimension = self.dimension
        self._generate()

    # Vector dimension options
    dimension_items = [
        ('2', 'Vec2', 'Two-dimensional vector'),
        ('3', 'Vec3', 'Three-dimensional vector'),
        ('4', 'Vec4', 'Four-dimensional vector (with w component)')
    ]
    
    dimension: bpy.props.EnumProperty(
        name="Dimensions",
        description="Vector dimensions",
        items=dimension_items,
        default='3',
        update=update_dimensions
    )
    
    value_x: bpy.props.FloatProperty(default=0.0, update=update_value)
    value_y: bpy.props.FloatProperty(default=0.0, update=update_value)
    value_z: bpy.props.FloatProperty(default=0.0, update=update_value)
    value_w: bpy.props.FloatProperty(default=0.0, update=update_value)

    def draw(self, context, layout):
        layout.prop(self, "dimension", text="")
        
        col = layout.column(align=True)
        col.prop(self, "value_x", text="")
        col.prop(self, "value_y", text="")
        
        if self.dimension in ('3', '4'):
            col.prop(self, "value_z", text="")
            
        if self.dimension == '4':
            col.prop(self, "value_w", text="")

    def on_create(self):
        self.add_output("ScriptingVectorSocket")
        # Initialize the socket dimension to match the node
        if hasattr(self, "outputs") and len(self.outputs) > 0:
            self.outputs[0].dimension = self.dimension

    def generate(self):
        if self.dimension == '2':
            self.outputs[0].code = f"({self.value_x}, {self.value_y})"
        elif self.dimension == '3':
            self.outputs[0].code = f"({self.value_x}, {self.value_y}, {self.value_z})"
        else:  # dimension == '4'
            self.outputs[0].code = f"({self.value_x}, {self.value_y}, {self.value_z}, {self.value_w})"