import bpy
import mathutils
from .base_socket import ScriptingSocket



class SN_FloatVectorSocket(bpy.types.NodeSocket, ScriptingSocket):

    bl_idname = "SN_FloatVectorSocket"
    group = "DATA"
    bl_label = "Float Vector"


    default_python_value = "(1.0, 1.0, 1.0)"
    default_prop_value = tuple([1.0]*32)

    def get_python_repr(self):
        return f"{tuple(getattr(self, self.subtype_attr))[:self.size]}"
    
    
    def _get_value(self):
        value = ScriptingSocket._get_value(self)
        value = tuple(map(lambda x: float(x), value))
        value = list(value)
        while len(value) < 32:
            value.append(1.0)
        return tuple(value)
    
    def _set_value(self, value):
        value = list(value)
        while len(value) < self.size:
            value.append(1.0)
        value = value[:self.size]
        ScriptingSocket._set_value(self, tuple(value))
        
    def update_size(self, context):
        self.default_python_value = str(tuple([1]*self.size))
        self._set_value(self.default_value)
        self.node.on_socket_type_change(self)
        
    def on_subtype_update(self):
        if self.subtype == "COLOR":
            self.size = 3
        elif self.subtype == "COLOR_ALPHA":
            self.size = 4

    size: bpy.props.IntProperty(default=3, min=2, max=32,
                                name="Size",
                                description="Size of this float vector",
                                update=update_size)
    
    size_editable: bpy.props.BoolProperty(default=False,
                                name="Size Editable",
                                description="Let's you edit the vectors size on the socket")

    default_value: bpy.props.FloatVectorProperty(name="Value",
                                            size=32,
                                            description="Value of this socket",
                                            get=_get_value,
                                            set=_set_value)

    color_value: bpy.props.FloatVectorProperty(name="Value",
                                            description="Value of this socket",
                                            size=3, min=0, max=1,
                                            default=(0.5,0.5,0.5),
                                            subtype="COLOR",
                                            update=ScriptingSocket._update_value)

    color_alpha_value: bpy.props.FloatVectorProperty(name="Value",
                                            description="Value of this socket",
                                            size=4, min=0, max=1,
                                            default=(0.5,0.5,0.5,0.5),
                                            subtype="COLOR",
                                            update=ScriptingSocket._update_value)


    subtypes = ["NONE", "COLOR", "COLOR_ALPHA"]
    subtype_values = {"NONE": "default_value", "COLOR": "color_value", "COLOR_ALPHA": "color_alpha_value"}
    

    def get_color(self, context, node):
        if "COLOR" in self.subtype:
            return (0.93, 0.85, 0.25)
        return (0.38, 0.34, 0.84)

    def draw_socket(self, context, layout, node, text, minimal=False):
        if self.is_output or self.is_linked:
            layout.label(text=text)
        elif self.subtype == "COLOR":
            col = layout.column(heading=text, align=True)
            col.prop(self, "color_value", text="")
        elif self.subtype == "COLOR_ALPHA":
            col = layout.column(heading=text, align=True)
            col.prop(self, "color_alpha_value", text="")
        else:
            col = layout.column(heading=text, align=True)
            for i in range(self.size):
                col.prop(self, self.subtype_attr, index=i, text="", toggle=True)
                
        if self.size_editable:
            layout.prop(self, "size", text="")