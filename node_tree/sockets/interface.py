import bpy
from .base_socket import ScriptingSocket

    
    
class SN_InterfaceSocket(bpy.types.NodeSocket, ScriptingSocket):
    
    bl_idname = "SN_InterfaceSocket"
    output_limit = 1
    socket_shape = "DIAMOND"
    is_program = True
    bl_label = "Interface"
    default_python_value = ""
    
    passthrough_layout_type: bpy.props.BoolProperty(default=False,
                                                description="Pass through layout type of the node before",
                                                name="Pass Through Layout Type")

    def get_color(self, context, node):
        return (0.9, 0.6, 0)
    
    def draw_socket(self, context, layout, node, text, minimal=False):
        layout.label(text=text)