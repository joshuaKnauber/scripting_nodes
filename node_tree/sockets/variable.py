import bpy
from .base_sockets import ScriptingSocket, DynamicSocket
from ...compiler.compiler import process_node



class SN_VariableSocket(bpy.types.NodeSocket, ScriptingSocket):
    bl_label = "Variable"
    sn_type = "VARIABLE"
    connects_to = ["SN_StringSocket","SN_DataSocket","SN_BooleanSocket","SN_FloatSocket", "SN_IntSocket"]

    def update_name(self,context):
        print("name")

    name: bpy.props.StringProperty(update=update_name)

    def update(self,node,link):
        if self.is_output and not self.name and not self.name == link.to_socket.name:
            self.name = link.to_socket.name
    
    def get_value(self, indents=0):
        return process_node(self.node, self)

    def draw_socket(self, context, layout, row, node, text):
        row.prop(self, "name", text="")

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