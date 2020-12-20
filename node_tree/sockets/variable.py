import bpy
from .base_sockets import ScriptingSocket, DynamicSocket
from ...compiler.compiler import process_node



class SN_VariableSocket(bpy.types.NodeSocket, ScriptingSocket):
    bl_label = "Variable"
    sn_type = "VARIABLE"
    connects_to = ["SN_StringSocket","SN_DataSocket","SN_BooleanSocket","SN_FloatSocket", "SN_IntSocket"]
    
    def get_value(self, indents=0):
        return " "*indents*4 + self.name

    def draw_socket(self, context, layout, row, node, text):
        row.label(text="text")

    def draw_color(self, context, node):
        if self.is_linked:
            if self.is_output:
                return self.links[0].to_socket.draw_color(context, self.links[0].to_node)
            else:
                return self.links[0].from_socket.draw_color(context, self.links[0].from_node)
        return (0.5,0.5,0.5,0.5)
    


class SN_DynamicVariableSocket(bpy.types.NodeSocket, DynamicSocket):
    connects_to = ["SN_StringSocket", "SN_DataSocket","SN_BooleanSocket","SN_FloatSocket","SN_IntSocket"]
    dynamic_overwrite = "SN_VariableSocket"