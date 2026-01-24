from ...base_node import ScriptingBaseNode
from .....lib.utils.node_tree.scripting_node_trees import node_by_id
from .....lib.utils.code.format import indent
import bpy


class SNA_OT_FloatVectorPropertySettings(bpy.types.Operator):
    """Configure float vector property settings"""

    bl_idname = "sna.float_vector_property_settings"
    bl_label = "Float Vector Property Settings"
    bl_description = "Configure float vector property options"
    bl_options = {"REGISTER", "INTERNAL"}

    node_id: bpy.props.StringProperty()
    show_options: bpy.props.BoolProperty(default=False)

    def draw(self, context):
        layout = self.layout
        node = node_by_id(self.node_id)
        if not node:
            layout.label(text="Node not found")
            return

        # Basic settings
        layout.prop(node, "prop_description")

        # Size
        layout.separator()
        layout.prop(node, "prop_size")

        # Default values
        layout.separator()
        layout.label(text="Default Values:")
        if node.prop_size >= 1:
            layout.prop(node, "prop_default_x", text="X")
        if node.prop_size >= 2:
            layout.prop(node, "prop_default_y", text="Y")
        if node.prop_size >= 3:
            layout.prop(node, "prop_default_z", text="Z")
        if node.prop_size >= 4:
            layout.prop(node, "prop_default_w", text="W")

        layout.separator()

        # Value limits
        layout.label(text="Hard Limits:")
        row = layout.row(align=True)
        row.prop(node, "prop_min", text="Min")
        row.prop(node, "prop_max", text="Max")

        layout.label(text="Soft Limits:")
        row = layout.row(align=True)
        row.prop(node, "prop_soft_min", text="Min")
        row.prop(node, "prop_soft_max", text="Max")

        layout.separator()

        # Step and precision
        layout.prop(node, "prop_step")
        layout.prop(node, "prop_precision")

        layout.separator()

        # Subtype
        layout.prop(node, "prop_subtype")

        layout.separator()

        # Name override
        layout.prop(node, "prop_name_override", text="Name Override")

        layout.separator()

        # Options toggle section
        box = layout.box()
        row = box.row()
        row.prop(
            self,
            "show_options",
            text="Options",
            icon="TRIA_DOWN" if self.show_options else "TRIA_RIGHT",
            emboss=False,
        )

        if self.show_options:
            col = box.column(align=True)
            col.prop(node, "option_hidden", toggle=True)
            col.prop(node, "option_skip_save", toggle=True)
            col.prop(node, "option_animatable", toggle=True)
            col.prop(node, "option_library_editable", toggle=True)

    def execute(self, context):
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=300)


class SNA_Node_FloatVectorProperty(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_FloatVectorProperty"
    bl_label = "Float Vector Property"

    def update_props(self, context):
        self._generate()

    def update_size(self, context):
        # Update default value display when size changes
        self._generate()

    # Property settings
    prop_name_override: bpy.props.StringProperty(
        name="Name Override",
        description="Override the auto-generated property name (leave empty to use generated name)",
        default="",
        update=update_props,
    )

    @property
    def prop_name(self):
        """Returns the property name - either the override or a generated name from label and id"""
        if self.prop_name_override:
            return self.prop_name_override
        import re

        label_clean = re.sub(r"[^a-zA-Z0-9_]", "_", self.prop_label.lower())
        label_clean = re.sub(r"_+", "_", label_clean).strip("_")
        if not label_clean:
            label_clean = "prop"
        return f"{label_clean}_{self.id}"

    register_on: bpy.props.EnumProperty(
        items=[
            ("Scene", "Scene", "Register on Scene", "SCENE_DATA", 0),
            ("Object", "Object", "Register on Object", "OBJECT_DATA", 1),
            ("Mesh", "Mesh", "Register on Mesh", "MESH_DATA", 2),
            ("Material", "Material", "Register on Material", "MATERIAL", 3),
            ("Light", "Light", "Register on Light", "LIGHT", 4),
            ("Camera", "Camera", "Register on Camera", "CAMERA_DATA", 5),
            ("World", "World", "Register on World", "WORLD", 6),
            (
                "Collection",
                "Collection",
                "Register on Collection",
                "OUTLINER_COLLECTION",
                7,
            ),
            ("Armature", "Armature", "Register on Armature", "ARMATURE_DATA", 8),
            ("Curve", "Curve", "Register on Curve", "CURVE_DATA", 9),
            ("Lattice", "Lattice", "Register on Lattice", "LATTICE_DATA", 10),
            ("Text", "Text", "Register on Text", "TEXT", 11),
            ("Action", "Action", "Register on Action", "ACTION", 12),
            ("NodeTree", "Node Tree", "Register on Node Tree", "NODETREE", 13),
            (
                "WindowManager",
                "Window Manager",
                "Register on Window Manager (global state)",
                "WINDOW",
                14,
            ),
        ],
        name="Register On",
        description="Blender data type to register this property on",
        default="Scene",
        update=update_props,
    )

    prop_label: bpy.props.StringProperty(
        name="Label",
        description="Display name of the property",
        default="My Vector",
        update=update_props,
    )

    prop_description: bpy.props.StringProperty(
        name="Description",
        description="Tooltip for the property",
        default="",
        update=update_props,
    )

    prop_size: bpy.props.IntProperty(
        name="Size",
        description="Size of the vector (1-4 components)",
        default=3,
        min=1,
        max=4,
        update=update_size,
    )

    # Default values for each component
    prop_default_x: bpy.props.FloatProperty(
        name="Default X",
        description="Default value for X component",
        default=0.0,
        update=update_props,
    )

    prop_default_y: bpy.props.FloatProperty(
        name="Default Y",
        description="Default value for Y component",
        default=0.0,
        update=update_props,
    )

    prop_default_z: bpy.props.FloatProperty(
        name="Default Z",
        description="Default value for Z component",
        default=0.0,
        update=update_props,
    )

    prop_default_w: bpy.props.FloatProperty(
        name="Default W",
        description="Default value for W component",
        default=0.0,
        update=update_props,
    )

    prop_min: bpy.props.FloatProperty(
        name="Min",
        description="Hard minimum value",
        default=-3.402823e38,
        update=update_props,
    )

    prop_max: bpy.props.FloatProperty(
        name="Max",
        description="Hard maximum value",
        default=3.402823e38,
        update=update_props,
    )

    prop_soft_min: bpy.props.FloatProperty(
        name="Soft Min",
        description="Soft minimum value (UI limit)",
        default=-1.0,
        update=update_props,
    )

    prop_soft_max: bpy.props.FloatProperty(
        name="Soft Max",
        description="Soft maximum value (UI limit)",
        default=1.0,
        update=update_props,
    )

    prop_step: bpy.props.IntProperty(
        name="Step",
        description="Step of increment/decrement in UI (actual value is /100)",
        default=3,
        min=1,
        max=100,
        update=update_props,
    )

    prop_precision: bpy.props.IntProperty(
        name="Precision",
        description="Number of decimal digits to display",
        default=2,
        min=0,
        max=6,
        update=update_props,
    )

    prop_subtype: bpy.props.EnumProperty(
        items=[
            ("NONE", "None", "Plain vector"),
            ("COLOR", "Color", "Color vector (0-1 range)"),
            ("TRANSLATION", "Translation", "Translation vector"),
            ("DIRECTION", "Direction", "Direction vector"),
            ("VELOCITY", "Velocity", "Velocity vector"),
            ("ACCELERATION", "Acceleration", "Acceleration vector"),
            ("MATRIX", "Matrix", "Matrix vector"),
            ("EULER", "Euler", "Euler rotation"),
            ("QUATERNION", "Quaternion", "Quaternion rotation"),
            ("AXISANGLE", "Axis Angle", "Axis angle rotation"),
            ("XYZ", "XYZ", "XYZ coordinates"),
            ("COLOR_GAMMA", "Color Gamma", "Color with gamma correction"),
            ("LAYER", "Layer", "Layer bitflag"),
            ("LAYER_MEMBER", "Layer Member", "Layer membership"),
        ],
        name="Subtype",
        description="Subtype of the float vector property",
        default="NONE",
        update=update_props,
    )

    # Property options
    option_hidden: bpy.props.BoolProperty(
        name="Hidden",
        description="Hide this property from the UI",
        default=False,
        update=update_props,
    )

    option_skip_save: bpy.props.BoolProperty(
        name="Skip Save",
        description="Don't save this property value",
        default=False,
        update=update_props,
    )

    option_animatable: bpy.props.BoolProperty(
        name="Animatable",
        description="Allow this property to be animated",
        default=True,
        update=update_props,
    )

    option_library_editable: bpy.props.BoolProperty(
        name="Library Editable",
        description="Allow editing this property for linked data",
        default=False,
        update=update_props,
    )

    # Fixed data type for reference system
    @property
    def data_type(self):
        return "ScriptingVectorSocket"

    def on_create(self):
        # Output for update callback
        self.add_output("ScriptingLogicSocket", "On Update")
        self.add_output("ScriptingBlendDataSocket", "Update Source")

    def draw(self, context, layout):
        layout.prop(self, "register_on", text="")
        layout.prop(self, "prop_label", text="Label")

        # Settings button
        op = layout.operator(
            "sna.float_vector_property_settings", text="Settings", icon="PREFERENCES"
        )
        op.node_id = self.id

    def generate(self):
        # Build options set
        options = []
        if self.option_hidden:
            options.append("'HIDDEN'")
        if self.option_skip_save:
            options.append("'SKIP_SAVE'")
        if self.option_animatable:
            options.append("'ANIMATABLE'")
        if self.option_library_editable:
            options.append("'LIBRARY_EDITABLE'")
        options_str = "{" + ", ".join(options) + "}" if options else "set()"

        # Check if update callback is connected
        update_socket = self.outputs.get("On Update")
        has_update = update_socket and update_socket.is_linked

        # Build default tuple based on size
        default_components = []
        if self.prop_size >= 1:
            default_components.append(str(self.prop_default_x))
        if self.prop_size >= 2:
            default_components.append(str(self.prop_default_y))
        if self.prop_size >= 3:
            default_components.append(str(self.prop_default_z))
        if self.prop_size >= 4:
            default_components.append(str(self.prop_default_w))
        default_str = "(" + ", ".join(default_components) + ")"

        # Build property definition code
        prop_args = [
            f'name="{self.prop_label}"',
            f'description="{self.prop_description}"',
            f"default={default_str}",
            f"size={self.prop_size}",
        ]

        # Add limits if not default
        if self.prop_min > -3.4e38:
            prop_args.append(f"min={self.prop_min}")
        if self.prop_max < 3.4e38:
            prop_args.append(f"max={self.prop_max}")

        prop_args.append(f"soft_min={self.prop_soft_min}")
        prop_args.append(f"soft_max={self.prop_soft_max}")
        prop_args.append(f"step={self.prop_step}")
        prop_args.append(f"precision={self.prop_precision}")

        if self.prop_subtype != "NONE":
            prop_args.append(f"subtype='{self.prop_subtype}'")

        prop_args.append(f"options={options_str}")

        if has_update:
            prop_args.append(f"update=update_{self.prop_name}")

        args_str = ",\n        ".join(prop_args)

        # Generate update callback if connected
        update_code = ""
        if has_update:
            update_body = indent(update_socket.eval("pass"), 2)
            update_code = f"""
def update_{self.prop_name}(self, context):
    {update_body}
"""
            # Set output codes for update function parameters
            self.outputs["Update Source"].code = "self"

        self.code_global = f"""
{update_code}
"""

        self.code_register = f"""
bpy.types.{self.register_on}.{self.prop_name} = bpy.props.FloatVectorProperty(
    {args_str}
)
"""

        self.code_unregister = f"""
del bpy.types.{self.register_on}.{self.prop_name}
"""
