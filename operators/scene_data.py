import bpy
from ..handler.socket_handler import SocketHandler

def add_data_output(node,label,is_output,use_four_numbers,prop_type="", is_color=False):
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
            socket = sockets.create_input(node,"VECTOR",label)
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
    bl_label = "Add output"
    bl_description = "Adds the selected output"
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
                        add_data_output(node,self.socket_name, self.is_output, self.use_four_numbers, prop.type, self.is_color)
        return {"FINISHED"}


class SN_OT_RemoveSceneDataSocket(bpy.types.Operator):
    bl_idname = "scripting_nodes.remove_scene_data_socket"
    bl_label = "Remove output"
    bl_description = "Removes the selected output"
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