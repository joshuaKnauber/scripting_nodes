import bpy

class SN_StringSocket(bpy.types.NodeSocket):
    '''String Socket for handling text'''
    bl_idname = 'SN_StringSocket'
    bl_label = "String"
    socket_color: bpy.props.FloatVectorProperty(size=4) # set in socket handler

    def is_valid(self,value):
        return value

    def make_valid(self,value):
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

    is_python_name: bpy.props.BoolProperty(default=False)

    def value(self):
        return self.socket_value

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text=text)
        else:
            layout.prop(self, "socket_value", text=text)

    def draw_color(self, context, node):
        return self.socket_color

