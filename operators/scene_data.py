import bpy
from ..handler.socket_handler import SocketHandler

def add_data_output(node, label, is_output, prop_type="", use_four_numbers=False, is_color=False):
    sockets = SocketHandler()
    if prop_type == "STRING" or prop_type == "ENUM":
        if is_output:
            sockets.create_output(node,"STRING",label)
        else:
            sockets.create_input(node,"STRING",label)
    elif prop_type == "BOOLEAN" or prop_type == str(bpy.types.BoolProperty):
        if is_output:
            sockets.create_output(node,"BOOLEAN",label)
        else:
            sockets.create_input(node,"BOOLEAN",label)
    elif prop_type == "VECTOR":
        if is_output:
            socket = sockets.create_output(node,"VECTOR",label)
            socket.use_four_numbers = use_four_numbers
            socket.is_color = is_color
        else:
            socket = sockets.create_input(node,"VECTOR",label)
            socket.use_four_numbers = use_four_numbers
            socket.is_color = is_color
    elif prop_type == "INT":
        if is_output:
            sockets.create_output(node,"INTEGER",label)
        else:
            sockets.create_input(node,"INTEGER",label)
    elif prop_type == "FLOAT":
        if is_output:
            sockets.create_output(node,"FLOAT",label)
        else:
            sockets.create_input(node,"FLOAT",label)
    elif prop_type == "COLLECTION":
        if is_output:
            sockets.create_output(node,"COLLECTION",label)
        else:
            sockets.create_input(node,"COLLECTION",label)
    else:
        if is_output:
            sockets.create_output(node,"OBJECT",label)
        else:
            sockets.create_input(node,"OBJECT",label)


class SN_OT_AddSceneDataSocket(bpy.types.Operator):
    bl_idname = "scripting_nodes.add_scene_data_socket"
    bl_label = "Add socket"
    bl_description = "Adds the selected socket"
    bl_options = {"REGISTER","INTERNAL"}

    node_name: bpy.props.StringProperty()
    socket_name: bpy.props.StringProperty()
    is_output: bpy.props.BoolProperty()
    use_four_numbers: bpy.props.BoolProperty()
    is_color: bpy.props.BoolProperty()

    def execute(self, context):
        for node in context.space_data.node_tree.nodes:
            if node.name == self.node_name:
                for prop in node.search_properties:
                    if prop.name == self.socket_name:
                        add_data_output(node,self.socket_name, self.is_output, prop.type, self.use_four_numbers, self.is_color)
        return {"FINISHED"}


class SN_OT_RemoveSceneDataSocket(bpy.types.Operator):
    bl_idname = "scripting_nodes.remove_scene_data_socket"
    bl_label = "Remove socket"
    bl_description = "Removes the selected socket"
    bl_options = {"REGISTER","INTERNAL"}

    node_name: bpy.props.StringProperty()
    socket_name: bpy.props.StringProperty()

    def execute(self, context):
        for node in context.space_data.node_tree.nodes:
            if node.name == self.node_name:
                for output in node.outputs:
                    if output.name == self.socket_name:
                        node.outputs.remove(output)
                for inp in node.inputs:
                    if inp.name == self.socket_name:
                        node.inputs.remove(inp)
        return {"FINISHED"}


class SN_OT_AddCustomSocket(bpy.types.Operator):
    bl_idname = "scripting_nodes.add_custom_socket"
    bl_label = "Add socket"
    bl_description = "Adds the selected socket"
    bl_options = {"REGISTER","INTERNAL"}

    node_name: bpy.props.StringProperty()
    is_output: bpy.props.BoolProperty()
    propName: bpy.props.StringProperty()
    propType: bpy.props.EnumProperty(items=[("STRING", "String", ""), ("STRING", "Enum", ""), ("BOOLEAN", "Boolean", ""), ("VECTOR", "Vector", ""), ("INTEGER", "Integer", ""), ("FLOAT", "Float", "")], name="Type", description="The type of the property")

    def draw(self, context):
        layout = self.layout
        layout.prop(self, "propName", text="Property Identifier")
        layout.prop(self, "propType")
        box = layout.box()
        box.alert = True
        box.label(text="Warning: You will need to put in the python identifier of your property!")

    def execute(self, context):
        for node in context.space_data.node_tree.nodes:
            if node.name == self.node_name:
                if self.is_output:
                    node.sockets.create_output(node,self.propType,self.propName)
                else:
                    node.sockets.create_input(node,self.propType,self.propName)
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_props_dialog(self, width=400)

