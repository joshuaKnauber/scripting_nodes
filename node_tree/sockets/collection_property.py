import bpy
from .base_socket import ScriptingSocket
from ...settings.data_properties import bpy_to_path_sections, bpy_to_indexed_sections, join_sections



class SN_CollectionPropertySocket(bpy.types.NodeSocket, ScriptingSocket):

    bl_idname = "SN_CollectionPropertySocket"
    group = "DATA"
    bl_label = "Collection Property"
    socket_shape = "SQUARE"


    default_python_value = "None"
    default_prop_value = ""
    
    def get_python_repr(self):
        return self.default_python_value
    
    
    @property
    def python_attr(self):
        sections = bpy_to_path_sections(self.python_value)
        if sections:
            return sections[-1]
        return self.python_value
    
    @property
    def python_source(self):
        sections = bpy_to_path_sections(self.python_value)
        if sections:
            if "bpy." in self.python_value: sections.insert(0, "bpy")
            return join_sections(sections[:-1])
        return self.python_value
    
    @property
    def python_sections(self):
        sections = bpy_to_path_sections(self.python_value)
        if sections:
            if "bpy." in self.python_value: sections.insert(0, "bpy")
            return sections
        return []


    subtypes = ["NONE"]
    subtype_values = {"NONE": "default_value"}
    

    def get_color(self, context, node):
        return (0, 0.87, 0.7)

    def draw_socket(self, context, layout, node, text):
        layout.label(text=text)