import bpy
from .base_sockets import ScriptingSocket, DynamicSocket
from ...compiler.compiler import process_node



class SN_StringSocket(bpy.types.NodeSocket, ScriptingSocket):
    bl_label = "String"
    sn_type = "STRING"

    def make_absolute(self,context):
        if self.file_path and not self.file_path == bpy.path.abspath(self.file_path):
            self.file_path = bpy.path.abspath(self.file_path)
        if self.dir_path and not self.dir_path == bpy.path.abspath(self.dir_path):
            self.dir_path = bpy.path.abspath(self.dir_path)
    
    def update_all(self,context):
        self.node.socket_value_update(context)
        self.make_absolute(context)
        if '"' in self.default_value:
            self.default_value = self.default_value.replace('"',"'")
        if '"' in self.file_path:
            self.file_path = self.file_path.replace('"',"'")
        if '"' in self.dir_path:
            self.dir_path = self.dir_path.replace('"',"'")
    
    default_value: bpy.props.StringProperty(default="",
                                            update=update_all,
                                            name="Value",
                                            description="Value of this socket")
    
    file_path: bpy.props.StringProperty(default="",
                                        subtype="FILE_PATH",
                                        update=update_all,
                                        name="Value",
                                        description="Value of this socket")
    
    dir_path: bpy.props.StringProperty(default="",
                                        subtype="DIR_PATH",
                                        update=update_all,
                                        name="Value",
                                        description="Value of this socket")
    
    #TODO add enum socket
    
    is_file_path: bpy.props.BoolProperty(default=False)
    is_dir_path: bpy.props.BoolProperty(default=False)
     
    def set_default(self, value):
        self.default_value = value
        self.file_path = value
        self.dir_path = value
        
    def get_return_value(self):
        if self.is_file_path:
            return self.file_path
        elif self.is_dir_path:
            return self.dir_path
        return self.default_value
    
    def process_value(self,value):
        if value and value[0] == '"' and value[-1] == '"':
            value = value[1:-1]
        value = value.replace('"',"'")
        return f"\"{value}\""
    
    def cast_value(self,value):
        return f"str({value})"

    def draw_socket(self, context, layout, row, node, text):
        if self.is_output or self.is_linked:
            row.label(text=text)
        else:
            if self.is_file_path:
                row.prop(self, "file_path", text=text)
            elif self.is_dir_path:
                row.prop(self, "dir_path", text=text)
            else:
                row.prop(self, "default_value", text=text)

    def draw_color(self, context, node):
        c = (0.3, 1, 0.3)
        if self.is_linked:
            return (c[0], c[1], c[2], 1)
        return (c[0], c[1], c[2], 0.5)
    


class SN_DynamicStringSocket(bpy.types.NodeSocket, DynamicSocket):
    add_idname = "SN_StringSocket"