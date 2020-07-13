import bpy

class SN_Socket:
    _is_data_socket = False
    socket_color: bpy.props.FloatVectorProperty(size=4)
    socket_type: bpy.props.StringProperty()
    uid: bpy.props.StringProperty(default="")
    dynamic: bpy.props.BoolProperty(default=False)
    dynamic_parent: bpy.props.StringProperty(default="")

    def draw_color(self, context, node):
        return self.socket_color




class SN_StringSocket(bpy.types.NodeSocket, SN_Socket):
    '''String Socket for handling text'''
    bl_idname = 'SN_StringSocket'
    bl_label = "String"
    _is_data_socket = True

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




class SN_BoolSocket(bpy.types.NodeSocket, SN_Socket):
    '''Bool Socket for handling booleans'''
    bl_idname = 'SN_BoolSocket'
    bl_label = "Boolean"
    _is_data_socket = True

    socket_value: bpy.props.BoolProperty(
        name="Boolean",
        description="Socket for a boolean value",
        default=True
    )

    show_toggle: bpy.props.BoolProperty(default=True)

    def get_value(self):
        return self.socket_value

    def set_value(self,value):
        self.socket_value = value

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text=text)
        else:
            layout.prop(self, "socket_value", text=text, toggle=self.show_toggle)




class SN_IntSocket(bpy.types.NodeSocket, SN_Socket):
    '''Int Socket for handling integers'''
    bl_idname = 'SN_IntSocket'
    bl_label = "Integer"
    _is_data_socket = True

    socket_value: bpy.props.IntProperty(
        name="Integer",
        description="Socket for an integer value",
        default=1
    )

    positive_value: bpy.props.IntProperty(
        name="Integer",
        description="Socket for an integer value",
        default=1,
        min=0
    )

    only_positive: bpy.props.BoolProperty(default=False)

    def get_value(self):
        if self.only_positive:
            return self.positive_value
        else:
            return self.socket_value

    def set_value(self,value):
        self.socket_value = value
        if value >= 0:
            self.positive_value = value
        else:
            self.positive_value = 0

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text=text)
        else:
            if self.only_positive:
                layout.prop(self, "positive_value", text=text)
            else:
                layout.prop(self, "socket_value", text=text)




class SN_FloatSocket(bpy.types.NodeSocket, SN_Socket):
    '''Float Socket for handling floats'''
    bl_idname = 'SN_FloatSocket'
    bl_label = "Float"
    _is_data_socket = True

    socket_value: bpy.props.FloatProperty(
        name="Float",
        description="Socket for a float value",
        default=1
    )

    factor_value: bpy.props.FloatProperty(
        name="Float",
        description="Socket for a float value",
        default=0.5,
        min=0,
        max=1
    )

    use_factor: bpy.props.BoolProperty(default=False)

    def get_value(self):
        if self.use_factor:
            return self.factor_value
        else:
            return self.socket_value

    def set_value(self,value):
        self.socket_value = value
        if value >= 0:
            if value <= 1:
                self.factor_value = value
            else:
                value = 1
        else:
            self.positive_value = 0

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text=text)
        else:
            if self.use_factor:
                layout.prop(self, "factor_value", text=text, slider=True)
            else:
                layout.prop(self, "socket_value", text=text)




class SN_VectorSocket(bpy.types.NodeSocket, SN_Socket):
    '''Vector Socket for handling vectors'''
    bl_idname = 'SN_VectorSocket'
    bl_label = "Vector"
    _is_data_socket = True

    socket_value: bpy.props.FloatVectorProperty(
        name="Vector",
        description="Socket for a vector value",
        default=(0,0,0),
        size=3
    )

    socket_value_quad: bpy.props.FloatVectorProperty(
        name="Vector",
        description="Socket for a vector value",
        default=(0,0,0,0),
        size=4
    )

    color_value: bpy.props.FloatVectorProperty(
        name="Color",
        description="Socket for a color value",
        default=(1,1,1),
        size=3,
        min=0,
        max=1,
        subtype="COLOR"
    )

    color_alpha_value: bpy.props.FloatVectorProperty(
        name="Color",
        description="Socket for a color value",
        default=(1,1,1,1),
        size=4,
        min=0,
        max=1,
        subtype="COLOR"
    )

    is_color: bpy.props.BoolProperty(default=False)

    use_four_digits: bpy.props.BoolProperty(default=False)

    def get_value(self):
        if self.is_color:
            if self.use_four_digits:
                return self.color_alpha_value
            else:
                return self.color_value
        else:
            if self.use_four_digits:
                return self.socket_value_quad
            else:
                return self.socket_value

    def clamp(self,digit):
        return max(0, min(digit, 1))

    def set_value(self,value):
        self.socket_value = value
        self.socket_value_quad = value
        if self.is_color:
            if self.use_four_digits:
                self.color_alpha_value = (self.clamp(value[0]),self.clamp(value[1]),self.clamp(value[2]),self.clamp(value[3]))
            else:
                self.color_value = (self.clamp(value[0]),self.clamp(value[1]),self.clamp(value[2]))

    def draw(self, context, layout, node, text):
        if self.is_output or self.is_linked:
            layout.label(text=text)
        else:
            if self.is_color:
                if self.use_four_digits:
                    layout.prop(self, "color_alpha_value", text=text)
                else:
                    layout.prop(self, "color_value", text=text)
            else:
                layout = layout.column()
                if self.use_four_digits:
                    layout.prop(self, "socket_value_quad", text=text)
                else:
                    layout.prop(self, "socket_value", text=text)



class SN_ExecuteSocket(bpy.types.NodeSocket, SN_Socket):
    '''Execute Socket for running the program'''
    bl_idname = 'SN_ExecuteSocket'
    bl_label = "Execute"
    _is_data_socket = False

    def draw(self, context, layout, node, text):
        layout.label(text=text)




class SN_LayoutSocket(bpy.types.NodeSocket, SN_Socket):
    '''Layout Socket for laying out ui'''
    bl_idname = 'SN_LayoutSocket'
    bl_label = "Layout"
    _is_data_socket = False

    def draw(self, context, layout, node, text):
        layout.label(text=text)




class SN_SeparatorSocket(bpy.types.NodeSocket, SN_Socket):
    '''Separator Socket for separating inputs of a node'''
    bl_idname = 'SN_SeparatorSocket'
    bl_label = "Separator"
    _is_data_socket = False

    def draw(self, context, layout, node, text):
        layout.label(text=text)