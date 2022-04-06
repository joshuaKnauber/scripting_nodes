import bpy
from .base_socket import ScriptingSocket
from ...settings.data_properties import bpy_to_path_sections, bpy_to_indexed_sections, join_sections



blend_data_defaults = {
    "Scenes": {
        "value": "bpy.context.scene",
        "name": "Using Active"},
    "Scene": {
        "value": "bpy.context.scene",
        "name": "Using Active"},
    "Objects": {
        "value": "bpy.context.active_object",
        "name": "Using Active"},
    "Object": {
        "value": "bpy.context.active_object",
        "name": "Using Active"},
    "Areas": {
        "value": "bpy.context.area",
        "name": "Using Active"},
    "Area": {
        "value": "bpy.context.area",
        "name": "Using Active"},
    "View Layers": {
        "value": "bpy.context.view_layer",
        "name": "Using Active"},
    "View Layer": {
        "value": "bpy.context.view_layer",
        "name": "Using Active"},
        
    "Preferences": {
        "value": lambda: "bpy.context.preferences.addons[__name__.partition('.')[ 0]].preferences" if bpy.context.scene.sn.is_exporting else "bpy.context.scene.sna_addon_prefs_temp",
        "name": "Using Self"},
    "Operator": {
        "value": "self",
        "name": "Using Self"},
}



class SN_PropertySocket(bpy.types.NodeSocket, ScriptingSocket):

    bl_idname = "SN_PropertySocket"
    group = "DATA"
    bl_label = "Property"


    @property
    def default_python_value(self):
        if self.name in blend_data_defaults:
            value = blend_data_defaults[self.name]["value"]
            if type(value) == str: return value
            else: return value()
        return "None"
    
    default_prop_value = ""

    def get_python_repr(self):
        return self.default_python_value
    
    
    @property
    def python_attr(self):
        sections = bpy_to_path_sections(self.python_value, True)
        if sections:
            return sections[-1]
        return self.python_value if self.python_value else "None"
    
    @property
    def python_source(self):
        sections = bpy_to_path_sections(self.python_value, True)
        if sections:
            if "bpy." in self.python_value: sections.insert(0, "bpy")
            path = join_sections(sections[:-1])
            if path: return path
        return self.python_value if self.python_value else "None"
    
    @property
    def python_sections(self):
        sections = bpy_to_path_sections(self.python_value, True)
        if sections:
            if "bpy." in self.python_value: sections.insert(0, "bpy")
            return sections
        return []
    
    
    subtypes = ["NONE"]
    subtype_values = {"NONE": "default_value"}
    

    def get_color(self, context, node):
        return (0, 0.87, 0.7)

    def draw_socket(self, context, layout, node, text):
        if not self.is_output and not self.is_linked:
            if self.name in blend_data_defaults:
                text += f" ({blend_data_defaults[self.name]['name']})"
            else:
                text += " (No Data)"
        layout.label(text=text)