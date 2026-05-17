"""Addon Preferences container node.

Emits a `bpy.types.AddonPreferences` subclass for the generated addon. The
class body picks up properties from any property nodes whose `register_on`
is set to "Preferences" and listed on this node's property list. The Draw
output socket lets the user lay out the preferences UI graphically.

Only one Preferences node per tree makes sense (the generated addon has
one preferences class), but we don't hard-enforce that - extra ones would
just emit duplicate classes that fail registration.
"""
from .....lib.utils.code.format import indent
from ...base_node import ScriptingBaseNode
from ..._class_body import ClassBodyContainerMixin
import bpy


class SNA_Node_Preferences(
    ClassBodyContainerMixin, ScriptingBaseNode, bpy.types.Node
):
    bl_idname = "SNA_Node_Preferences"
    bl_label = "Preferences"
    sn_options = {"ROOT_NODE"}

    def on_create(self):
        # Draw output - what to render inside the preferences panel
        self.add_output("ScriptingInterfaceSocket", "Draw")

    def draw(self, context, layout):
        self.draw_class_body_properties(layout, label="Properties")

    def generate(self):
        # Annotations from attached property nodes (Preferences-targeted only)
        annotations = []
        for entry, prop_node in self.iter_attached_property_nodes():
            if getattr(prop_node, "register_on", "") != "Preferences":
                continue
            line = prop_node.class_body_annotation()
            if line:
                annotations.append(line)

        # bl_idname must match the addon's package name so Blender resolves
        # context.preferences.addons[__package__].preferences correctly.
        # __package__ is the top-level module name at runtime.
        class_attrs = ['bl_idname = __package__']
        class_attrs.extend(annotations)
        attrs_code = "\n    ".join(class_attrs)

        draw_socket = self.outputs.get("Draw")
        draw_socket.layout = f"prefs_layout_{self.id}"
        draw_body = draw_socket.eval("pass")

        self.code_module = f"""
class SNA_AP_Preferences_{self.id}(bpy.types.AddonPreferences):
    {attrs_code}

    def draw(self, context):
        prefs_layout_{self.id} = self.layout
        {indent(draw_body, 2)}
"""
