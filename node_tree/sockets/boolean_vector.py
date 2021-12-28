import bpy
import mathutils
from .base_socket import ScriptingSocket



class SN_BooleanVectorSocket(bpy.types.NodeSocket, ScriptingSocket):

    bl_idname = "SN_BooleanVectorSocket"
    group = "DATA"
    bl_label = "Boolean Vector"


    default_python_value = "(False, False, False)"
    default_prop_value = tuple([False]*32)

    def get_python_repr(self):
        return f"{tuple(getattr(self, self.subtype_attr))[:self.size]}"
    
    
    def _get_value(self):
        value = ScriptingSocket._get_value(self)
        value = tuple(map(lambda x: bool(x), value))
        return tuple(value)
    
    def _set_value(self, value):
        value = list(value)
        while len(value) < 32:
            value.append(False)
        ScriptingSocket._set_value(self, tuple(value))
        
    def update_size(self, context):
        self.default_python_value = str(tuple([False]*self.size))
        self._set_value(self.default_value)

    size: bpy.props.IntProperty(default=3, min=2, max=32,
                                name="Size",
                                description="Size of this boolean vector",
                                update=update_size)

    default_value: bpy.props.BoolVectorProperty(name="Value",
                                            size=32,
                                            description="Value of this socket",
                                            get=_get_value,
                                            set=_set_value)

    subtypes = ["NONE"]
    subtype_values = {"NONE": "default_value"}
    
    
    def get_color(self, context, node):
        return (0.38, 0.34, 0.84)

    def draw_socket(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text=text)
        else:
            col = layout.column(heading=text, align=True)
            for i in range(self.size):
                col.prop(self, self.subtype_attr, index=i, text=str(getattr(self, self.subtype_attr)[i]), toggle=True)