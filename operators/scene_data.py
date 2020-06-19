import bpy

def add_data_output(self,prop,label,prop_type=""):
    if prop:
        prop_type = str(type(prop))
    if prop_type == str(str) or prop_type in [str(bpy.types.StringProperty),str(bpy.types.EnumProperty)]:
        out = self.outputs.new('SN_StringSocket', label)
    elif prop_type == str(bool) or prop_type == str(bpy.types.BoolProperty):
        out = self.outputs.new('SN_BooleanSocket', label)
    elif prop_type == str(tuple):# or prop_type in [str(bpy.types.FloatVectorProperty)]:
        out = self.outputs.new('SN_VectorSocket', label)
    elif prop_type == str(int) or prop_type == str(bpy.types.IntProperty):
        out = self.outputs.new('SN_IntSocket', label)
    elif prop_type == str(float) or prop_type == str(bpy.types.FloatProperty):
        out = self.outputs.new('SN_FloatSocket', label)
    else:
        out = self.outputs.new('SN_SceneDataSocket', label)
        out.display_shape = "SQUARE"


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
                        add_data_output(node,None,self.socket_name,prop.type)
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