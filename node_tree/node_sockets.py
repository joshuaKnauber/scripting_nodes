import bpy

class SN_StringSocket(bpy.types.NodeSocket):
    '''String Socket for handling text'''
    bl_idname = 'SN_StringSocket'
    bl_label = "String"
    socket_color: bpy.props.FloatVectorProperty(size=4) # set in socket handler

    _invalid_chars = [" ","\\","-","?",".",",","<",">","*","+","-","#","'","~","@","€","|","\"","²",
                    "³","§","$","%","&","/","(","[","]",")","=","}","{","´","´","^","°",":",";"]

    def is_valid(self,value):
        if value:
            if not self.is_python_name:
                return True
            else:
                for char in self._invalid_chars:
                    if char in value:
                        return False
                return True
        return False

    def make_valid(self,value):
        if self.is_python_name:
            for char in self._invalid_chars:
                value = value.replace(char,"")
            if not value:
                value = "name"
        return value

    def update_socket_value(self,context):
        if not self.is_valid(self.socket_value):
            self.socket_value = self.make_valid(self.socket_value)

    socket_value: bpy.props.StringProperty(
        name="String",
        description="Socket for a string value",
        default="",
        update=update_socket_value
    )

    is_python_name: bpy.props.BoolProperty(default=False,update=update_socket_value)

    def get_value(self):
        return self.socket_value

    def set_value(self,value):
        self.socket_value = value

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text=text)
        else:
            layout.prop(self, "socket_value", text=text)

    def draw_color(self, context, node):
        return self.socket_color

