import bpy
from ...node_sockets import update_socket_autocompile
from ..base_node import SN_ScriptingBaseNode
from ..node_looks import node_colors, node_icons
from .scene_nodes_utils import add_data_output, get_active_types
from ..node_utility import get_types
from ...properties.search_properties import SN_SearchPropertyGroup


class SN_DataPropertiesNode(bpy.types.Node, SN_ScriptingBaseNode):
    '''Scene Data Properties Node for outputting the properties of scene data'''
    bl_idname = 'SN_DataPropertiesNode'
    bl_label = "Data Properties"
    bl_icon = node_icons["SCENE"]

    previous_connection: bpy.props.StringProperty(default="")
    current_data_type: bpy.props.StringProperty(default="")
    search_value: bpy.props.StringProperty(default="")

    search_properties: bpy.props.CollectionProperty(type=SN_SearchPropertyGroup)

    def get_data_name(self,name):
        if name.split("_")[0] == "active":
            active_types = get_active_types()
            for date in active_types:
                if active_types[date] == name.split("_")[-1]:
                    name = date
        return name

    def generate_sockets(self):
        if len(self.inputs[0].links) > 0:
            if self.inputs[0].links[0].from_socket.bl_idname == "SN_SceneDataSocket":

                if self.previous_connection != self.inputs[0].links[0].from_socket.name:

                    self.previous_connection = self.inputs[0].links[0].from_socket.name
                    for socket in self.outputs:
                        self.outputs.remove(socket)
                    self.search_properties.clear()

                    code = ("").join(self.inputs[0].links[0].from_node.evaluate(self.inputs[0].links[0].from_socket)["code"])

                    ignore_props = ["RNA","Display Name","Full Name"]

                    types = get_types()
                    data = self.get_data_name(code.split(".")[-1])

                    for data_type in types:
                        if types[data_type] == data:
                            self.current_data_type = data_type
                            for prop in eval("bpy.types."+data_type+".bl_rna.properties"):
                                if not prop.name in ignore_props:
                                    item = self.search_properties.add()
                                    item.name = prop.name
                                    item.propType = str(type(prop))
        else:
            for socket in self.outputs:
                self.outputs.remove(socket)
            self.search_properties.clear()

    def get_prop_identifier(self,name):
        for prop in eval("bpy.types."+self.current_data_type+".bl_rna.properties"):
            if prop.name == name:
                return prop.identifier
        return None

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["INPUT"]

        inp = self.inputs.new('SN_SceneDataSocket', "Scene Data")
        inp.display_shape = "SQUARE"

        self.generate_sockets()

    def update(self):
        self.search_value = ""
        self.generate_sockets()

    def copy(self, node):
        pass# called when node is copied

    def free(self):
        pass# called when node is removed

    def draw_buttons(self, context, layout):
        row = layout.row(align=True)
        row.prop_search(self,"search_value",self,"search_properties",text="")

        has_output = False
        for out in self.outputs:
            if out.name == self.search_value:
                has_output = True

        if not has_output and not self.search_value == "":
            op = row.operator("scripting_nodes.add_scene_data_socket",text="",icon="ADD")
            op.node_name = self.name
            op.socket_name = self.search_value
        if has_output:
            op = row.operator("scripting_nodes.remove_scene_data_socket",text="",icon="REMOVE")
            op.node_name = self.name
            op.socket_name = self.search_value

    def evaluate(self, output):
        code = []
        errors = []

        if self.inputs[0].is_linked:
            if self.inputs[0].links[0].from_socket.bl_idname == "SN_SceneDataSocket":
                identifier = self.get_prop_identifier(output.name)
                if identifier:
                    code.append(self.inputs[0].links[0].from_socket)
                    code.append(".")
                    code.append(identifier)# add for loop for multiple data blocks
            else:
                errors.append("wrong_socket")
        return {"code": code, "error":errors}
        
        