from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
import bpy


class SNA_Node_In_Mode(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_In_Mode"
    bl_label = "In Mode"

    def update_value(self, context):
        self._generate()

    mode_options = [
        ("EDIT_MESH", "Edit Mesh", "Is in Edit Mesh mode?"),
        ("EDIT_CURVE", "Edit Curve", "Is in Edit Curve mode?"),
        ("EDIT_CURVES", "Edit Hair Curves", "Is in Edit Hair Curves mode?"),
        ("EDIT_SURFACE", "Edit Surface", "Is in Edit Surface mode?"),
        ("EDIT_TEXT", "Edit Text", "Is in Edit Text mode?"),
        ("EDIT_ARMATURE", "Edit Armature", "Is in Edit Armature mode?"),
        ("EDIT_METABALL", "Edit Metaball", "Is in Edit Metaball mode?"),
        ("EDIT_LATTICE", "Edit Lattice", "Is in Edit Lattice mode?"),
        ("EDIT_POINT_CLOUD", "Edit Point Cloud", "Is in Edit Point Cloud mode?"),
        ("POSE", "Pose", "Is in Pose mode?"),
        ("SCULPT", "Sculpt", "Is in Sculpt mode?"),
        ("PAINT_WEIGHT", "Paint Weight", "Is in Paint Weight mode?"),
        ("PAINT_VERTEX", "Paint Vertex", "Is in Paint Vertex mode?"),
        ("PAINT_TEXTURE", "Paint Texture", "Is in Paint Texture mode?"),
        ("PARTICLE", "Particle", "Is in Particle mode?"),
        ("OBJECT", "Object", "Is in Object mode?"),
        ("SCULPT_CURVES", "Sculpt Curves", "Is in Sculpt Curves mode?")
    ]
    
    blender_version = bpy.app.version

    if blender_version < (4, 3, 0) and blender_version >= (3, 0, 0):
        gpencil_modes = [
            ("EDIT_GPENCIL", "Edit Grease Pencil", "Is in Edit Grease Pencil mode?"),
            ("SCULPT_GPENCIL", "Sculpt Grease Pencil", "Is in Sculpt Grease Pencil mode?"),
            ("WEIGHT_GPENCIL", "Weight Vertex Grease Pencil", "Is in Weight Vertex Grease Pencil mode?"),
            ("PAINT_GPENCIL", "Paint Grease Pencil", "Is in Paint Grease Pencil mode?"),
            ("VERTEX_GPENCIL", "Vertex Grease Pencil", "Is in Vertex Grease Pencil mode?")
        ]

        mode_options.extend(gpencil_modes)
    else:
        gpencil_modes = [
            ("EDIT_GREASE_PENCIL", "Edit Grease Pencil", "Is in Edit Grease Pencil mode?"),
            ("SCULPT_GREASE_PENCIL", "Sculpt Grease Pencil", "Is in Sculpt Grease Pencil mode?"),
            ("WEIGHT_GREASE_PENCIL", "Weight Vertex Grease Pencil", "Is in Weight Vertex Grease Pencil mode?"),
            ("PAINT_GREASE_PENCIL", "Paint Grease Pencil", "Is in Paint Grease Pencil mode?"),
            ("VERTEX_GREASE_PENCIL", "Vertex Grease Pencil", "Is in Vertex Grease Pencil mode?")
        ]

        mode_options.extend(gpencil_modes)
    
    in_mode: bpy.props.EnumProperty(
        items=mode_options, name="Mode", update=update_value
    )

    def on_create(self):
        self.add_output("ScriptingBooleanSocket", label="Result")

    def draw(self, context, layout):      
        layout.prop(self, "in_mode", text="")

    def generate(self):
        self.outputs[0].code = f"bpy.context.mode == '{self.in_mode}'"

