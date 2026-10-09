import bpy

from ....core import functions
from ....core.context import NodeError
from ....core import naming
from ..._reference_signatures import PROPERTY_GROUP_NODES
from ._property_base import PropertyNode

POINTER_TYPES = [
    ("Object", "Object", "Any Blender object"),
    ("Mesh", "Mesh", "Mesh data"),
    ("Material", "Material", "Material data"),
    ("Image", "Image", "Image data"),
    ("Texture", "Texture", "Texture data"),
    ("NodeTree", "Node Tree", "Node tree data"),
    ("Collection", "Collection", "Collection data"),
    ("Camera", "Camera", "Camera data"),
    ("Light", "Light", "Light data"),
    ("World", "World", "World data"),
    ("Armature", "Armature", "Armature data"),
    ("Curve", "Curve", "Curve data"),
    ("Lattice", "Lattice", "Lattice data"),
    ("GreasePencil", "Grease Pencil", "Grease Pencil data"),
    ("Text", "Text", "Text data"),
    ("Action", "Action", "Animation action"),
    ("Brush", "Brush", "Brush data"),
    ("ParticleSettings", "Particle Settings", "Particle system settings"),
    ("Scene", "Scene", "Scene data"),
    ("Screen", "Screen", "Screen layout"),
    ("WindowManager", "Window Manager", "Window manager"),
]

POINTER_SOURCES = [
    ("BLENDER", "Blender Type", "A built-in Blender data type", "BLENDER", 0),
    (
        "PROPERTY_GROUP",
        "Property Group",
        "A Property Group node of this addon",
        "OUTLINER_DATA_POINTCLOUD",
        1,
    ),
]


def _is_function(self, tree):
    return tree.bl_idname == "ScriptingNodeTree" and functions.is_function(tree)


class GroupTypeMixin:
    """`group`: the Property Group node used as type (Pointer/Collection)."""

    sn_reference_properties = {"group": PROPERTY_GROUP_NODES}

    group: bpy.props.StringProperty(name="Property Group")

    def uses_group(self):
        return True

    def group_node(self):
        """The referenced Property Group node, if this property uses one."""
        return self.resolve_reference("group") if self.uses_group() else None

    def group_type(self, ctx) -> str:
        group = self.group_node()
        if group is None:
            raise NodeError("Pick a property group")
        return ctx.symbol(group, group.class_name)


class SNA_Node_PointerProperty(GroupTypeMixin, PropertyNode, bpy.types.Node):
    bl_idname = "SNA_Node_PointerProperty"
    bl_label = "Pointer Property"
    bpy_type = "PointerProperty"
    data_type = "ScriptingBlendDataSocket"
    supported_options = ("HIDDEN", "SKIP_SAVE", "LIBRARY_EDITABLE")

    prop_label: bpy.props.StringProperty(name="Label", default="My Pointer")
    pointer_source: bpy.props.EnumProperty(
        items=POINTER_SOURCES, name="Source", default="BLENDER"
    )
    prop_type: bpy.props.EnumProperty(
        items=POINTER_TYPES, name="Type", description="Blender type it points to"
    )
    poll_function: bpy.props.PointerProperty(
        type=bpy.types.NodeTree,
        name="Poll Function",
        description=(
            "Function (group) deciding which items can be picked: gets the "
            "item as first input (and self), returns True to allow it"
        ),
        poll=_is_function,
    )

    def uses_group(self):
        return self.pointer_source == "PROPERTY_GROUP"

    def uses_poll(self):
        # Blender only filters ID pointers
        return self.poll_function is not None and not self.uses_group()

    def sn_names(self):
        return super().sn_names() + [naming.Symbol("poll", f"poll_{self.prop_name}")]

    def poll_function_name(self):
        return self.sn_name("poll")

    def property_args(self, ctx):
        if self.uses_group():
            args = [f"type={self.group_type(ctx)}"]
        else:
            args = [f"type=bpy.types.{self.prop_type}"]
        if self.uses_poll():
            args.append(f"poll={ctx.symbol(self, self.poll_function_name())}")
        return args

    def emit(self, ctx):
        if self.uses_group():
            self.group_type(ctx)  # show a missing group on this node
        if self.uses_poll():
            tree = self.poll_function
            function = ctx.symbol(tree, tree.function_name)
            args = "object, self=self" if functions.parameters(tree) else "self=self"
            ctx.module(f"""
                def {self.poll_function_name()}(self, object):
                    return bool({function}({args}))
            """)
        super().emit(ctx)

    def draw_node(self, context, layout):
        layout.prop(self, "pointer_source", text="")
        if self.uses_group():
            self.draw_reference_prop(layout, "group", text="Group")
        else:
            layout.prop(self, "prop_type", text="")

    def draw_settings(self, layout):
        if not self.uses_group():
            layout.prop(self, "poll_function")
