"""PropertyGroup container node.

Emits a `bpy.types.PropertyGroup` subclass. Properties whose `register_on`
is "PropertyGroup" can be attached via this node's Properties list, and
their annotations get injected into the emitted class body. The class
itself registers automatically through auto_load (it's a PropertyGroup
subclass), so we don't emit code_register/code_unregister - we just need
the class to exist in the module.

Other nodes (Collection Property, Pointer Property) reference this node
through the standard ref system; they read `class_name` to wire up
`type=<class>` in their bpy.props.* calls.
"""
import re
from .....lib.utils.code.format import indent
from ...base_node import ScriptingBaseNode
from ..._class_body import ClassBodyContainerMixin
from ..._reference_signatures import PROPERTY_NODES
import bpy


def _sanitize_name(label: str) -> str:
    cleaned = re.sub(r"[^a-zA-Z0-9_]", "_", label)
    cleaned = re.sub(r"_+", "_", cleaned).strip("_")
    return cleaned or "PropertyGroup"


class SNA_Node_PropertyGroup(
    ClassBodyContainerMixin, ScriptingBaseNode, bpy.types.Node
):
    bl_idname = "SNA_Node_PropertyGroup"
    bl_label = "Property Group"
    sn_options = {"ROOT_NODE"}
    sn_class_body_signature = PROPERTY_NODES

    def update_props(self, context):
        self._generate()

    prop_label: bpy.props.StringProperty(
        name="Label",
        description="Display name for this property group (used to derive its class name)",
        default="My Group",
        update=update_props,
    )

    @property
    def class_name(self):
        """Emitted class name. Used by Collection/Pointer Property nodes to
        wire `type=<class>` in their bpy.props.* calls."""
        addon = bpy.context.scene.sna.addon
        return f"{addon.class_prefix}_PG_{_sanitize_name(self.prop_label)}_{self.id}"

    def on_create(self):
        # No sockets - this node is purely a class definition. Other nodes
        # reference it by name via the standard ref system.
        pass

    def draw(self, context, layout):
        layout.prop(self, "prop_label", text="Label")
        self.draw_class_body_properties(layout, label="Properties")

    def generate(self):
        annotations = []
        for entry, prop_node in self.iter_attached_property_nodes():
            if getattr(prop_node, "register_on", "") != "PropertyGroup":
                continue
            line = prop_node.class_body_annotation()
            if line:
                annotations.append(line)

        if annotations:
            body = "\n    ".join(annotations)
        else:
            body = "pass"

        self.code_module = f"""
class {self.class_name}(bpy.types.PropertyGroup):
    {body}
"""
