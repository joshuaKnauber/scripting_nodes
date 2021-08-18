import bpy
from .base_sockets import ScriptingSocket
from ...compiler.compiler import process_node



class SN_StringSocket(bpy.types.NodeSocket, ScriptingSocket):

    group = "DATA"
    bl_label = "String"
    socket_type = "STRING"
    
    
    enum_values: bpy.props.StringProperty()

    is_set: bpy.props.BoolProperty(default=False)

    can_edit_items: bpy.props.BoolProperty(default=False)
    
    def enum_items(self,context):
        items = []
        if self.enum_values:
            items = eval(self.enum_values)
        if not items:
            items = [("NONE","None","No items have been found for this property")]
        return items


    def update_string(self, context):
        if self.value and self.value[-1] == "\\":
            self["value"] = self.value[:-1] + "/"
        self["value"] = self.value.replace("\"", "'")
        self.auto_compile()

    def make_absolute(self,context):
        if not self.value_directory == bpy.path.abspath(self.value_directory):
            self.value_directory = bpy.path.abspath(self.value_directory)
        if not self.value_file == bpy.path.abspath(self.value_file):
            self.value_file = bpy.path.abspath(self.value_file)

        if self.value_directory and self.value_directory[-1] == "\\":
            self["value_directory"] = self.value_directory[:-1] + "/"
        self["value_directory"] = self.value_directory.replace("\"", "'")
        if self.value_file and self.value_file[-1] == "\\":
            self["value_file"] = self.value_file[:-1] + "/"
        self["value_file"] = self.value_file.replace("\"", "'")
        self.auto_compile()


    value: bpy.props.StringProperty(name="Value",
                                    description="Value of this socket",
                                    update=update_string)

    value_file: bpy.props.StringProperty(name="Value",
                                        description="Value of this socket",
                                        subtype="FILE_PATH",
                                        update=make_absolute)

    value_directory: bpy.props.StringProperty(name="Value",
                                        description="Value of this socket",
                                        subtype="DIR_PATH",
                                        update=make_absolute)

    value_enum: bpy.props.EnumProperty(name="Value",
                                        description="Value of this socket",
                                        items=enum_items,
                                        update=ScriptingSocket.auto_compile)
    
    
    subtype: bpy.props.EnumProperty(items=[("NONE","None","None"),
                                            ("FILE","File","File"),
                                            ("DIRECTORY","Directory","Directory"),
                                            ("ENUM","Enum","Enum")])
    
    copy_attributes = ["value","value_file","value_directory","enum_values","value_enum"]
    
    
    def set_default(self,value):
        if self.subtype == "NONE":
            self.value = value
        elif self.subtype == "FILE":
            self.value_file = value
        elif self.subtype == "DIRECTORY":
            self.value_directory = value
        elif self.subtype == "ENUM":
            self.value = value
            for item in self.enum_items(bpy.context):
                if item[0] == value:
                    self.value_enum = value
    
    
    def default_value(self):
        if self.subtype == "NONE":
            return "r\"" + self.value + "\""
        elif self.subtype == "FILE":
            return "r\"" + self.value_file + "\""
        elif self.subtype == "DIRECTORY":
            return "r\"" + self.value_directory + "\""
        elif self.subtype == "ENUM":
            if self.enum_values:
                value = "sn_cast_enum(r\"" + self.value_enum + "\", " + self.enum_values + ")"
            else:
                value = "r\"" + self.value_enum + "\""
            if self.is_set:
                return "{" + value + "}"
            return value
    
    
    def convert_data(self, code):
        return "sn_cast_string(" + code + ")"


    def draw_socket(self, context, layout, row, node, text):
        if self.is_output or self.is_linked:
            row.label(text=text)
        else:
            if self.subtype == "NONE":
                row.prop(self, "value", text=text)
            elif self.subtype == "FILE":
                row.prop(self, "value_file", text=text)
            elif self.subtype == "DIRECTORY":
                row.prop(self, "value_directory", text=text)
            elif self.subtype == "ENUM":
                row.prop(self, "value_enum", text=text)


    def draw_variable_socket(self, layout):
        if self.can_edit_items and self.subtype == "ENUM":
            op = layout.operator("sn.edit_enum_socket_items", text="", icon="COLLAPSEMENU", emboss=False)
            op.node = self.node.name
            op.socket_index = self.get_socket_index()
            op.is_output = self.is_output


    def get_color(self, context, node):
        return (0.3, 1, 0.3)
    


class SN_DynamicStringSocket(bpy.types.NodeSocket, ScriptingSocket):
    group = "DATA"
    bl_label = "String"
    socket_type = "STRING"
    
    dynamic = True
    to_add_idname = "SN_StringSocket"
    
    subtype: bpy.props.EnumProperty(items=[("NONE","None","None"),
                                            ("FILE","File","File"),
                                            ("DIRECTORY","Directory","Directory"),
                                            ("ENUM","Enum","Enum")])
    
    
    def setup(self):
        self.addable = True



class SN_SimpleEnumItem(bpy.types.PropertyGroup):

    name: bpy.props.StringProperty(name="Name",
                                   description="The displayed name of your enum entry",
                                   default="My Item")

    
    description: bpy.props.StringProperty(name="Description",
                                   description="The tooltip of your enum entry",
                                   default="This is my enum item")



global_items = None
class SN_OT_AddEnumSocketItem(bpy.types.Operator):
    bl_idname = "sn.add_enum_socket_item"
    bl_label = "Add Item"
    bl_description = "Add an enum item to this socket"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def execute(self, context):
        global global_items
        if global_items != None:
            global_items.add() 
        return {"FINISHED"}


class SN_OT_RemoveEnumSocketItem(bpy.types.Operator):
    bl_idname = "sn.remove_enum_socket_item"
    bl_label = "Remove Item"
    bl_description = "Remove this enum item from this socket"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    index: bpy.props.IntProperty(options={"HIDDEN"})

    def execute(self, context):
        global global_items
        if global_items:
            global_items.remove(self.index) 
        return {"FINISHED"}


class SN_OT_MoveEnumSocketItem(bpy.types.Operator):
    bl_idname = "sn.move_enum_socket_item"
    bl_label = "Move Item"
    bl_description = "Move this enum item in this socket"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    index: bpy.props.IntProperty(options={"HIDDEN"})
    up: bpy.props.BoolProperty(options={"HIDDEN"})

    def execute(self, context):
        global global_items
        if global_items:
            if self.up:
                global_items.move(self.index, self.index-1) 
            else:
                global_items.move(self.index, self.index+1) 
        return {"FINISHED"}



class SN_OT_EditEnumSocketItems(bpy.types.Operator):
    bl_idname = "sn.edit_enum_socket_items"
    bl_label = "Edit Items"
    bl_description = "Edit the items of this sockets enum property"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    node: bpy.props.StringProperty(options={"HIDDEN"})
    socket_index: bpy.props.IntProperty(options={"HIDDEN"})
    is_output: bpy.props.BoolProperty(default=True, options={"HIDDEN"})

    items: bpy.props.CollectionProperty(type=SN_SimpleEnumItem)


    def get_node_socket(self, context):
        node = context.space_data.node_tree.nodes[self.node]
        if self.is_output:
            socket = node.outputs[self.socket_index]
        else:
            socket = node.inputs[self.socket_index]
        return socket


    def execute(self, context):
        node = context.space_data.node_tree.nodes[self.node]
        socket = self.get_node_socket(context)

        enum_string = node.enum_collection_to_string(self.items)

        socket.enum_values = enum_string
        socket.variable_name = socket.variable_name # trigger update
        return {"FINISHED"}


    def draw(self, context):
        layout = self.layout
        
        for index, item in enumerate(self.items):
            box = layout.box()
            col = box.column(align=True)
            row = col.row(align=True)
            row.prop(item, "name", text="Name")

            op = row.operator("sn.move_enum_socket_item", text="", icon="TRIA_UP")
            op.index = index
            op.up = True

            op = row.operator("sn.move_enum_socket_item", text="", icon="TRIA_DOWN")
            op.index = index
            op.up = False

            op = row.operator("sn.remove_enum_socket_item", text="", icon="PANEL_CLOSE")
            op.index = index

            col.prop(item, "description", text="Description")

        row = layout.row()
        row.scale_y = 1.2
        row.operator("sn.add_enum_socket_item", text="Add Item", icon="ADD")


    def invoke(self, context, event):
        socket = self.get_node_socket(context)

        items = []
        if socket.enum_values:
            items = eval(socket.enum_values)

        self.items.clear()
        for item in items:
            new = self.items.add()
            new.name = item[0]
            new.description = item[2]

        global global_items
        global_items = self.items
        return context.window_manager.invoke_props_dialog(self)