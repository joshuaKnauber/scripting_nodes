import bpy
from ..handler.socket_handler import SocketHandler

def add_data_output(node,label,prop_type=""):
    sockets = SocketHandler()
    if prop_type == "STRING" or prop_type == "ENUM":
        sockets.create_output(node,"STRING",label)
    elif prop_type == "BOOLEAN" or prop_type == str(bpy.types.BoolProperty):
        sockets.create_output(node,"BOOLEAN",label)
    elif prop_type == "VECTOR":
        sockets.create_output(node,"VECTOR",label)
    elif prop_type == "INT":
        sockets.create_output(node,"INTEGER",label)
    elif prop_type == "FLOAT":
        sockets.create_output(node,"FLOAT",label)
    elif prop_type == "POINTER":
        sockets.create_output(node,"OBJECT",label)
    elif prop_type == "COLLECTION":
        sockets.create_output(node,"COLLECTION",label)
    else:
        sockets.create_output(node,"OBJECT",label)


class SN_OT_AddSceneDataSocket(bpy.types.Operator):
    bl_idname = "scripting_nodes.add_scene_data_socket"
    bl_label = "Add output"
    bl_description = "Adds the selected output"
    bl_options = {"REGISTER","INTERNAL"}

    node_name: bpy.props.StringProperty()
    socket_name: bpy.props.StringProperty()

    def execute(self, context):
        for node in context.space_data.node_tree.nodes:
            if node.name == self.node_name:
                for prop in node.search_properties:
                    if prop.name == self.socket_name:
                        add_data_output(node,self.socket_name,prop.type)
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
        return {"FINISHED"}