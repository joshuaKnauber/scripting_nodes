import bpy
from .base_socket import ScriptingSocket
from ...settings.data_properties import (
    bpy_to_path_sections,
    bpy_to_indexed_sections,
    join_sections,
)


blend_data_defaults = {
    "Scenes": {"value": "bpy.context.scene", "name": "Using Active"},
    "Scene": {"value": "bpy.context.scene", "name": "Using Active"},
    "Objects": {
        "value": "bpy.context.view_layer.objects.active",
        "name": "Using Active",
    },
    "Object": {
        "value": "bpy.context.view_layer.objects.active",
        "name": "Using Active",
    },
    "Meshes": {
        "value": "bpy.context.view_layer.objects.active.data",
        "name": "Using Active",
    },
    "Mesh": {
        "value": "bpy.context.view_layer.objects.active.data",
        "name": "Using Active",
    },
    "Materials": {
        "value": "bpy.context.view_layer.objects.active.active_material",
        "name": "Using Active",
    },
    "Material": {
        "value": "bpy.context.view_layer.objects.active.active_material",
        "name": "Using Active",
    },
    "Areas": {"value": "bpy.context.area", "name": "Using Active"},
    "Area": {"value": "bpy.context.area", "name": "Using Active"},
    "Screens": {"value": "bpy.context.screen", "name": "Using Active"},
    "Screen": {"value": "bpy.context.screen", "name": "Using Active"},
    "View Layers": {"value": "bpy.context.view_layer", "name": "Using Active"},
    "View Layer": {"value": "bpy.context.view_layer", "name": "Using Active"},
    "Light": {"value": "bpy.context.view_layer.objects.active", "name": "Using Active"},
    "Lights": {
        "value": "bpy.context.view_layer.objects.active",
        "name": "Using Active",
    },
    "Camera": {
        "value": "bpy.context.view_layer.objects.active",
        "name": "Using Active",
    },
    "Cameras": {
        "value": "bpy.context.view_layer.objects.active",
        "name": "Using Active",
    },
    "Preferences": {
        "value": lambda: (
            f"bpy.context.preferences.addons[__package__].preferences"
            if bpy.context.scene.sn.is_exporting
            else "bpy.context.scene.sna_addon_prefs_temp"
        ),
        "name": "Using Self",
    },
    "Operator": {"value": "self", "name": "Using Self"},
    "Modal Operator": {"value": "self", "name": "Using Self"},
}


class SN_PropertySocket(bpy.types.NodeSocket, ScriptingSocket):

    bl_idname = "SN_PropertySocket"
    group = "DATA"
    bl_label = "Property"

    @property
    def default_python_value(self):
        if self.name in blend_data_defaults:
            value = blend_data_defaults[self.name]["value"]
            if type(value) == str:
                return value
            else:
                return value()
        return "None"

    default_prop_value = ""

    def get_python_repr(self):
        return self.default_python_value

    @property
    def python_attr(self):
        sections = bpy_to_path_sections(self.python_value)
        if sections:
            return sections[-1]
        return self.python_value if self.python_value else "None"

    @property
    def python_is_attribute(self):
        sections = bpy_to_path_sections(self.python_value)
        if sections:
            last_section = sections[-1].replace("'", '"')
            if last_section[0] == "[" and last_section[-1] == "]":
                return True
        return False

    @property
    def python_source(self):
        sections = bpy_to_path_sections(self.python_value)
        if sections:
            if self.python_value.startswith("bpy."):
                sections.insert(0, "bpy")
            path = join_sections(sections[:-1])
            if path:
                return path
        return self.python_value if self.python_value else "None"

    @property
    def python_sections(self):
        sections = bpy_to_path_sections(self.python_value)
        if sections:
            if self.python_value.startswith("bpy."):
                sections.insert(0, "bpy")
            return sections
        return []

    subtypes = ["NONE"]
    subtype_values = {"NONE": "default_value"}

    def get_color(self, context, node):
        return (0, 0.87, 0.7)

    def draw_socket(self, context, layout, node, text, minimal=False):
        if not self.is_output and not self.is_linked:
            if self.name in blend_data_defaults:
                text += f" ({blend_data_defaults[self.name]['name']})"
            else:
                text += " (No Data)"
        layout.label(text=text)
