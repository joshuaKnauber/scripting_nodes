from ...base_node import ScriptingBaseNode
from .....lib.utils.node_tree.scripting_node_trees import node_by_id
from .....lib.utils.code.format import indent
import bpy


class SNA_OT_EnumPropertySettings(bpy.types.Operator):
    """Configure enum property settings"""

    bl_idname = "sna.enum_property_settings"
    bl_label = "Enum Property Settings"
    bl_description = "Configure enum property options"
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

        layout.separator()

        # Default value
        layout.prop(node, "prop_default", text="Default Identifier")

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
            col.prop(node, "option_enum_flag", toggle=True)

    def execute(self, context):
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=300)


class SNA_Node_EnumProperty(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_EnumProperty"
    bl_label = "Enum Property"
    sn_reference_properties = {"items_variable"}

    def update_props(self, context):
        self._generate()

    def update_items_mode(self, context):
        # Update socket visibility based on mode
        items_socket = self.inputs.get("Items")
        if items_socket:
            items_socket.hide = self.items_mode == "DYNAMIC"

        # Update dynamic-related sockets visibility
        update_items_socket = self.outputs.get("Update Items")

        if update_items_socket:
            update_items_socket.hide = self.items_mode != "DYNAMIC"

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
        default="My Enum",
        update=update_props,
    )

    prop_description: bpy.props.StringProperty(
        name="Description",
        description="Tooltip for the property",
        default="",
        update=update_props,
    )

    prop_default: bpy.props.StringProperty(
        name="Default",
        description="Default value (identifier of the default item)",
        default="",
        update=update_props,
    )

    items_mode: bpy.props.EnumProperty(
        items=[
            ("STATIC", "Static", "Define items directly"),
            ("DYNAMIC", "Dynamic", "Use a function to generate items"),
        ],
        name="Items Mode",
        description="How to define enum items",
        default="STATIC",
        update=update_items_mode,
    )

    items_variable: bpy.props.StringProperty(
        name="Items Variable",
        description="Global variable containing the enum items list",
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

    option_enum_flag: bpy.props.BoolProperty(
        name="Enum Flag",
        description="Allow multiple items to be selected (creates a set of values)",
        default=False,
        update=update_props,
    )

    # Fixed data type for reference system
    @property
    def data_type(self):
        return "ScriptingStringSocket"

    def on_create(self):
        # Input for static items
        self.add_input("ScriptingListSocket", "Items")

        # Output for update callback
        self.add_output("ScriptingLogicSocket", "On Update")
        self.add_output("ScriptingBlendDataSocket", "Update Source")

        # Output for dynamic items function (hidden by default)
        update_items_socket = self.add_output("ScriptingLogicSocket", "Update Items")
        update_items_socket.hide = True

    def draw(self, context, layout):
        layout.prop(self, "register_on", text="")
        layout.prop(self, "prop_label", text="Label")
        layout.prop(self, "items_mode", text="")

        if self.items_mode == "DYNAMIC":
            layout.prop_search(
                self, "items_variable", context.scene.sna, "references", text="Variable"
            )

        # Settings button
        op = layout.operator(
            "sna.enum_property_settings", text="Settings", icon="PREFERENCES"
        )
        op.node_id = self.id

    def on_ref_change(self, node):
        self._generate()

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
        if self.option_enum_flag:
            options.append("'ENUM_FLAG'")
        options_str = "{" + ", ".join(options) + "}" if options else "set()"

        # Check if update callback is connected
        update_socket = self.outputs.get("On Update")
        has_update = update_socket and update_socket.is_linked

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

        if self.items_mode == "STATIC":
            # Static items - use items from input socket
            items_code = self.inputs["Items"].eval("[]")

            # Build property definition code
            prop_args = [
                f"items={items_code}",
                f'name="{self.prop_label}"',
                f'description="{self.prop_description}"',
            ]

            if self.prop_default:
                prop_args.append(f'default="{self.prop_default}"')

            prop_args.append(f"options={options_str}")

            if has_update:
                prop_args.append(f"update=update_{self.prop_name}")

            args_str = ",\n        ".join(prop_args)

            self.code_global = f"""
{update_code}
"""

            self.code_register = f"""
bpy.types.{self.register_on}.{self.prop_name} = bpy.props.EnumProperty(
    {args_str}
)
"""

        else:
            # Dynamic items - use a function
            update_items_socket = self.outputs.get("Update Items")
            has_update_items = update_items_socket and update_items_socket.is_linked

            # Get the variable reference for the items
            var_code = "[]"
            ref = bpy.context.scene.sna.references.get(self.items_variable)
            if ref:
                var_code = f"var_{ref.node_id}"

            # Generate the get items function
            if has_update_items:
                update_items_body = indent(
                    update_items_socket.eval(f"return {var_code}"), 2
                )
            else:
                update_items_body = f"return {var_code}"

            get_items_code = f"""
def get_items_{self.prop_name}(self, context):
    {update_items_body}
"""

            # Build property definition code
            prop_args = [
                f"items=get_items_{self.prop_name}",
                f'name="{self.prop_label}"',
                f'description="{self.prop_description}"',
            ]

            # Note: default is typically not used with dynamic items
            # as it can cause issues if the default doesn't exist

            prop_args.append(f"options={options_str}")

            if has_update:
                prop_args.append(f"update=update_{self.prop_name}")

            args_str = ",\n        ".join(prop_args)

            self.code_global = f"""
{update_code}{get_items_code}
"""

            self.code_register = f"""
bpy.types.{self.register_on}.{self.prop_name} = bpy.props.EnumProperty(
    {args_str}
)
"""

        self.code_unregister = f"""
del bpy.types.{self.register_on}.{self.prop_name}
"""
