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
        
        self.socket_shape = self.display_shape
        self.update_shape(context)
    
    data_type: bpy.props.StringProperty()

    data_type_collection: bpy.props.StringProperty()
    
    data_name: bpy.props.StringProperty()

    data_identifier: bpy.props.StringProperty() # optional
    
    subtype: bpy.props.EnumProperty(items=[("NONE","Data Block","Data Block"),
                                           ("COLLECTION","Collection","Collection")],
                                    update=update_subtype)

    copy_attributes = ["data_type", "data_type_collection", "data_name", "data_identifier"]
    
    def convert_data(self, code):
        return "sn_cast_blend_data(" + code + ")"
    
    def default_value(self):
        if self.subtype == "COLLECTION":
            return "[]"
        return "None"

    def draw_socket(self, context, layout, row, node, text):
        row.label(text=text)

    def get_color(self, context, node):
        return (0,1,0.8)
