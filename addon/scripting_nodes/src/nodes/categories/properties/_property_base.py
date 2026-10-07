"""Base of all property nodes (Integer Property, Enum Property, ...).

A property node registers a `bpy.props.*Property` either on a Blender type
(`bpy.types.Scene.my_value = ...` in register()) or, with register_on set to
Operator / Preferences / PropertyGroup, as an annotation in that node's class
(see nodes/_class_body.py).

Subclasses set `bpy_type` and `data_type`, add their own settings and
implement `property_args(ctx)` and `draw_settings(layout)`:

    class SNA_Node_IntProperty(PropertyNode, bpy.types.Node):
        bl_idname = "SNA_Node_IntProperty"
        bl_label = "Integer Property"
        bpy_type = "IntProperty"
        data_type = "ScriptingIntegerSocket"

        prop_default: bpy.props.IntProperty(name="Default")

        def property_args(self, ctx):
            return [f"default={self.prop_default}"]
"""

import bpy

from ....core.context import NodeError
from ....core.naming import function_name, identifier
from ....lib.code_format import literal_set
from ....lib.trees import node_by_id
from ....sockets.spec import BlendData, Logic
from ...base_node import ScriptingBaseNode

REGISTER_ON_ITEMS = [
    ("Scene", "Scene", "Register on Scene", "SCENE_DATA", 0),
    ("Object", "Object", "Register on Object", "OBJECT_DATA", 1),
    ("Mesh", "Mesh", "Register on Mesh", "MESH_DATA", 2),
    ("Material", "Material", "Register on Material", "MATERIAL", 3),
    ("Light", "Light", "Register on Light", "LIGHT", 4),
    ("Camera", "Camera", "Register on Camera", "CAMERA_DATA", 5),
    ("World", "World", "Register on World", "WORLD", 6),
    ("Collection", "Collection", "Register on Collection", "OUTLINER_COLLECTION", 7),
    ("Armature", "Armature", "Register on Armature", "ARMATURE_DATA", 8),
    ("Curve", "Curve", "Register on Curve", "CURVE_DATA", 9),
    ("Lattice", "Lattice", "Register on Lattice", "LATTICE_DATA", 10),
    ("Text", "Text", "Register on Text", "TEXT", 11),
    ("Action", "Action", "Register on Action", "ACTION", 12),
    ("NodeTree", "Node Tree", "Register on Node Tree", "NODETREE", 13),
    ("WindowManager", "Window Manager", "Register on Window Manager", "WINDOW", 14),
    ("Operator", "Operator", "Attach to an Operator node's class", "DOT", 15),
    ("Preferences", "Preferences", "Attach to the addon preferences", "PREFERENCES", 16),
    ("PropertyGroup", "Property Group", "Attach to a Property Group node", "OUTLINER_DATA_POINTCLOUD", 17),
]  # fmt: skip

CLASS_BODY_TARGETS = {"Operator", "Preferences", "PropertyGroup"}


class SNA_OT_PropertySettings(bpy.types.Operator):
    """Settings of a property node"""

    bl_idname = "sna.property_settings"
    bl_label = "Property Settings"
    bl_options = {"REGISTER", "INTERNAL"}

    node_id: bpy.props.StringProperty()

    def draw(self, context):
        node = node_by_id(self.node_id)
        if node is None:
            self.layout.label(text="Node not found")
            return
        node.draw_all_settings(self.layout)

    def execute(self, context):
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=300)


class PropertyNode(ScriptingBaseNode):
    """Shared settings, naming and code of property nodes."""

    sn_root = True
    sn_order = 20  # after property groups, before classes using them

    # bpy.props function and the socket type values of this property have
    bpy_type = ""
    data_type = "ScriptingDataSocket"
    # option flags this property type supports
    supported_options = ("HIDDEN", "SKIP_SAVE", "ANIMATABLE", "LIBRARY_EDITABLE")
    # whether the type supports an update callback
    has_update = True

    register_on: bpy.props.EnumProperty(items=REGISTER_ON_ITEMS, name="Register On")
    prop_label: bpy.props.StringProperty(name="Label", default="My Property")
    prop_description: bpy.props.StringProperty(name="Description")
    prop_name_override: bpy.props.StringProperty(
        name="Name Override", description="Python name of the property (optional)"
    )
    option_hidden: bpy.props.BoolProperty(name="Hidden")
    option_skip_save: bpy.props.BoolProperty(name="Skip Save")
    option_animatable: bpy.props.BoolProperty(name="Animatable", default=True)
    option_library_editable: bpy.props.BoolProperty(name="Library Editable")

    def socket_specs(self):
        if not self.has_update:
            return [], []
        return [], [
            Logic("on_update", "On Update"),
            BlendData("update_source", "Update Source"),
        ]

    # -- naming ---------------------------------------------------------------

    @property
    def prop_name(self):
        """Python name the property is registered under."""
        if self.prop_name_override:
            return identifier(self.prop_name_override)
        return f"{identifier(self.prop_label.lower(), 'prop')}_{self.id.lower()}"

    @property
    def is_class_body_target(self):
        return self.register_on in CLASS_BODY_TARGETS

    def update_function_name(self):
        return function_name(self, f"update_{self.prop_name}")

    def uses_update(self):
        socket = self.socket("on_update", output=True)
        return self.has_update and socket is not None and socket.is_linked

    # -- code -----------------------------------------------------------------

    def property_args(self, ctx) -> list[str]:
        """Type specific `key=value` arguments. `ctx` may belong to another
        node (the class this property is attached to)."""
        return []

    def _options(self):
        flags = {
            "HIDDEN": self.option_hidden,
            "SKIP_SAVE": self.option_skip_save,
            "ANIMATABLE": self.option_animatable,
            "LIBRARY_EDITABLE": self.option_library_editable,
        }
        return {
            flag for flag, on in flags.items() if on and flag in self.supported_options
        }

    def call(self, ctx) -> str:
        """`bpy.props.X(...)` for this property."""
        args = [f"name={self.prop_label!r}", f"description={self.prop_description!r}"]
        args += self.property_args(ctx)
        options = self._options()
        args.append(f"options={literal_set(options)}")
        if self.uses_update():
            # the class using this property may live in another tree's module
            args.append(f"update={ctx.symbol(self, self.update_function_name())}")
        return f"bpy.props.{self.bpy_type}({', '.join(args)})"

    def annotation(self, ctx) -> str:
        """`name: bpy.props.X(...)` for use in a class body."""
        return f"{self.prop_name}: {self.call(ctx)}"

    def emit(self, ctx):
        if self.uses_update():
            ctx.module(f"""
                def {self.update_function_name()}(self, context):
                    {ctx.flow("on_update", outputs={"update_source": "self"})}
            """)
        if not self.is_class_body_target:
            ctx.on_register(
                f"bpy.types.{self.register_on}.{self.prop_name} = {self.call(ctx)}"
            )
            ctx.on_unregister(f"del bpy.types.{self.register_on}.{self.prop_name}")

    def require(self, condition, message):
        if not condition:
            raise NodeError(message)

    # -- UI -------------------------------------------------------------------

    def draw(self, context, layout):
        layout.prop(self, "register_on", text="")
        layout.prop(self, "prop_label", text="Label")
        self.draw_node(context, layout)
        op = layout.operator(
            "sna.property_settings", text="Settings", icon="PREFERENCES"
        )
        op.node_id = self.id

    def draw_node(self, context, layout):
        """Extra settings shown on the node itself."""

    def draw_settings(self, layout):
        """Type specific settings in the settings popup."""

    def draw_all_settings(self, layout):
        layout.prop(self, "prop_description")
        self.draw_settings(layout)
        layout.prop(self, "prop_name_override")
        col = layout.column(heading="Options", align=True)
        for flag, prop in (
            ("HIDDEN", "option_hidden"),
            ("SKIP_SAVE", "option_skip_save"),
            ("ANIMATABLE", "option_animatable"),
            ("LIBRARY_EDITABLE", "option_library_editable"),
        ):
            if flag in self.supported_options:
                col.prop(self, prop)
