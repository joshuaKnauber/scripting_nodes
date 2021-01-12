import bpy
from .base_sockets import ScriptingSocket
from ...compiler.compiler import process_node



class SN_BlendDataSocket(bpy.types.NodeSocket, ScriptingSocket):
    
    group = "DATA"
    bl_label = "Blend Data"
    socket_type = "BLEND_DATA"
        
    def update_subtype(self,context):
        if self.subtype == "COLLECTION":
            self.display_shape = "SQUARE"
        else:
            self.display_shape = "CIRCLE"
    
    data_type: bpy.props.StringProperty()
    
    data_path: bpy.props.StringProperty()
    data_identifier: bpy.props.StringProperty()
    
    subtype: bpy.props.EnumProperty(items=[("DATA_BLOCK","Data Block","Data Block"),
                                           ("COLLECTION","Collection","Collection")],
                                    update=update_subtype)

    copy_attributes = ["data_type","data_path","data_identifier"]
    
    def convert_data(self, code):
        return "sn_cast_blend_data(" + code + ")"
    
    def default_value(self):
        return "None"

    def draw_socket(self, context, layout, row, node, text):
        row.label(text=text)

    def get_color(self, context, node):
        return (0,1,0.8)
