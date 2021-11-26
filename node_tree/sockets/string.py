import bpy
from .base_sockets import ScriptingSocket



class SN_StringSocket(bpy.types.NodeSocket, ScriptingSocket):

    group = "DATA"
    bl_label = "String"


    def get_value(self):
        if self.is_output:
            return self.get(self.subtype_attr, "")
        else:
            from_out = self.from_socket()
            if from_out:
                return from_out.default_value
            return self.get(self.subtype_attr, "")

    def set_value(self, value):
        self[self.subtype_attr] = value
        
        if self.is_output:
            for socket in self.to_sockets():
                socket.node.evaluate(bpy.context)
        else:
            self.node.evaluate(bpy.context)

    default_value: bpy.props.StringProperty(name="Value",
                                            description="Value of this socket",
                                            get=get_value,
                                            set=set_value)

    value_file_path: bpy.props.StringProperty(name="Value",
                                            description="Value of this socket",
                                            subtype="FILE_PATH")

    value_dir_path: bpy.props.StringProperty(name="Value",
                                            description="Value of this socket",
                                            subtype="DIR_PATH")

    subtypes = ["NONE", "FILE_PATH", "DIR_PATH"]
    subtype_values = {"NONE": "default_value", "FILE_PATH": "value_file_path", "DIR_PATH": "value_dir_path"}
    

    def get_color(self, context, node):
        return (0.44, 0.7, 1)

    def draw_socket(self, context, layout, node, text):
        text = self.get(self.subtype_attr, "")
        if self.is_output or self.is_linked:
            layout.label(text=text)
        else:
            layout.prop(self, "default_value", text=text)