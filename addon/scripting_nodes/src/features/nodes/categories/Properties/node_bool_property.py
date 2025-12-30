from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
from scripting_nodes.src.lib.utils.node_tree.scripting_node_trees import node_by_id
from scripting_nodes.src.lib.utils.code.format import indent
import bpy


class SNA_OT_BoolPropertySettings(bpy.types.Operator):
    """Configure boolean property settings"""

    bl_idname = "sna.bool_property_settings"
    bl_label = "Boolean Property Settings"
    bl_description = "Configure boolean property options"
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
        layout.prop(node, "prop_default")

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
        return context.window_manager.invoke_popup(self, width=250)


class SNA_Node_BoolProperty(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_BoolProperty"
    bl_label = "Boolean Property"

    def update_props(self, context):
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
        default="My Boolean",
        update=update_props,
    )

    prop_description: bpy.props.StringProperty(
        name="Description",
        description="Tooltip for the property",
        default="",
        update=update_props,
    )

    prop_default: bpy.props.BoolProperty(
        name="Default",
        description="Default value of the property",
        default=False,
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
        return "ScriptingBooleanSocket"

    def on_create(self):
        # Output for update callback
        self.add_output("ScriptingLogicSocket", "On Update")
        self.add_output("ScriptingBlendDataSocket", "Update Source")

    def draw(self, context, layout):
        layout.prop(self, "register_on", text="")
        layout.prop(self, "prop_label", text="Label")

        # Settings button
        op = layout.operator(
            "sna.bool_property_settings", text="Settings", icon="PREFERENCES"
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

        # Build property definition code
        prop_args = [
            f'name="{self.prop_label}"',
            f'description="{self.prop_description}"',
            f"default={self.prop_default}",
        ]

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
bpy.types.{self.register_on}.{self.prop_name} = bpy.props.BoolProperty(
    {args_str}
)
"""

        self.code_unregister = f"""
del bpy.types.{self.register_on}.{self.prop_name}
"""
