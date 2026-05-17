from ...base_node import ScriptingBaseNode
from .....lib.utils.node_tree.scripting_node_trees import node_by_id
from .....lib.utils.code.format import indent
from ._class_body_support import (
    CLASS_BODY_REGISTER_ON_ITEMS,
    is_class_body_target,
)
import bpy


class SNA_OT_CollectionPropertySettings(bpy.types.Operator):
    """Configure collection property settings"""

    bl_idname = "sna.collection_property_settings"
    bl_label = "Collection Property Settings"
    bl_description = "Configure collection property options"
    bl_options = {"REGISTER", "INTERNAL"}

    node_id: bpy.props.StringProperty()
    show_options: bpy.props.BoolProperty(default=False)

    def draw(self, context):
        layout = self.layout
        node = node_by_id(self.node_id)
        if not node:
            layout.label(text="Node not found")
            return

        layout.prop(node, "prop_description")
        layout.separator()
        layout.prop(node, "prop_name_override", text="Name Override")

        layout.separator()
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
            col.prop(node, "option_library_editable", toggle=True)

    def execute(self, context):
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=300)


class SNA_Node_CollectionProperty(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_CollectionProperty"
    bl_label = "Collection Property"
    sn_reference_properties = {"group"}

    def update_props(self, context):
        self._generate()

    prop_name_override: bpy.props.StringProperty(
        name="Name Override",
        description="Override the auto-generated property name",
        default="",
        update=update_props,
    )

    @property
    def prop_name(self):
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
            *CLASS_BODY_REGISTER_ON_ITEMS,
        ],
        name="Register On",
        description="Blender data type to register this property on",
        default="Scene",
        update=update_props,
    )

    @property
    def is_class_body_target(self):
        return is_class_body_target(self.register_on)

    prop_label: bpy.props.StringProperty(
        name="Label",
        description="Display name of the property",
        default="My Collection",
        update=update_props,
    )

    prop_description: bpy.props.StringProperty(
        name="Description",
        description="Tooltip for the property",
        default="",
        update=update_props,
    )

    # Reference to a Property Group container node providing the element type
    group: bpy.props.StringProperty(name="Property Group", update=update_props)

    option_hidden: bpy.props.BoolProperty(
        name="Hidden", default=False, update=update_props
    )
    option_skip_save: bpy.props.BoolProperty(
        name="Skip Save", default=False, update=update_props
    )
    option_library_editable: bpy.props.BoolProperty(
        name="Library Editable", default=False, update=update_props
    )

    @property
    def data_type(self):
        # Collections are reference-typed in our system - downstream Get/UI
        # nodes treat the collection as a blend-data-style handle.
        return "ScriptingBlendDataSocket"

    def on_create(self):
        # No sockets - collection access is via Get Property which reads
        # the registered attribute by name.
        pass

    def on_ref_change(self, node):
        self._generate()

    def draw(self, context, layout):
        layout.prop(self, "register_on", text="")
        layout.prop(self, "prop_label", text="Label")
        self.draw_reference_prop(layout, "group", text="Group")

        op = layout.operator(
            "sna.collection_property_settings", text="Settings", icon="PREFERENCES"
        )
        op.node_id = self.id

    def _resolve_group_class_name(self):
        target = self.resolve_reference("group")
        if target is None:
            return None
        return getattr(target, "class_name", None)

    def _build_prop_args(self):
        options = []
        if self.option_hidden:
            options.append("'HIDDEN'")
        if self.option_skip_save:
            options.append("'SKIP_SAVE'")
        if self.option_library_editable:
            options.append("'LIBRARY_EDITABLE'")
        options_str = "{" + ", ".join(options) + "}" if options else "set()"

        group_class = self._resolve_group_class_name()
        prop_args = []
        if group_class:
            prop_args.append(f"type={group_class}")
        prop_args.append(f'name="{self.prop_label}"')
        prop_args.append(f'description="{self.prop_description}"')
        if options_str != "set()":
            prop_args.append(f"options={options_str}")
        return prop_args, group_class

    def class_body_annotation(self):
        prop_args, group_class = self._build_prop_args()
        if not group_class:
            return ""
        return (
            f"{self.prop_name}: bpy.props.CollectionProperty("
            + ", ".join(prop_args)
            + ")"
        )

    def generate(self):
        prop_args, group_class = self._build_prop_args()

        # No group connected - skip emitting register/unregister so the
        # generated module stays valid. UI shows a warning.
        if not group_class:
            return

        if self.is_class_body_target:
            return

        args_str = ",\n        ".join(prop_args)
        self.code_register = f"""
bpy.types.{self.register_on}.{self.prop_name} = bpy.props.CollectionProperty(
    {args_str}
)
"""
        self.code_unregister = f"""
del bpy.types.{self.register_on}.{self.prop_name}
"""
