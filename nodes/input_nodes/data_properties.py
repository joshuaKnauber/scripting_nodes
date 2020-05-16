import bpy
from ...node_sockets import update_socket_autocompile
from ..base_node import SN_ScriptingBaseNode
from ..node_looks import node_colors, node_icons
from .scene_nodes_utils import add_data_output, get_active_types
from ..node_utility import get_types


class SN_DataPropertiesNode(bpy.types.Node, SN_ScriptingBaseNode):
    '''Scene Data Properties Node for outputting the properties of scene data'''
    bl_idname = 'SN_DataPropertiesNode'
    bl_label = "Data Properties"
    bl_icon = node_icons["SCENE"]

    def update_hide(self,context):
        for out in self.outputs:
            if self.hide_unused:
                out.hide = not out.is_linked
            else:
                out.hide = False

    hide_unused: bpy.props.BoolProperty(default=False,name="Hide Unused",description="Hides the unused outputs",update=update_hide)
    previous_connection: bpy.props.StringProperty(default="")
    current_data_type: bpy.props.StringProperty(default="")

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

                    code = ("").join(self.inputs[0].links[0].from_node.evaluate(self.inputs[0].links[0].from_socket)["code"])

                    ignore_props = ["RNA"]

                    types = get_types()
                    data = self.get_data_name(code.split(".")[-1])

                    for data_type in types:
                        if types[data_type] == data:
                            self.current_data_type = data_type
                            for prop in eval("bpy.types."+data_type+".bl_rna.properties"):
                                if not prop.name in ignore_props:
                                    add_data_output(self,prop,prop.name)
        else:
            for socket in self.outputs:
                self.outputs.remove(socket)

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
        self.generate_sockets()

    def copy(self, node):
        pass# called when node is copied

    def free(self):
        pass# called when node is removed

    def draw_buttons(self, context, layout):
        layout.prop(self,"hide_unused",toggle=True)

    def evaluate(self, output):
        code = []
        errors = []

        if self.inputs[0].is_linked:
            if self.inputs[0].links[0].from_socket.bl_idname == "SN_SceneDataSocket":
                identifier = self.get_prop_identifier(output.name)
                if identifier:
                    code.append(self.inputs[0].links[0].from_socket)
                    code.append(".")
                    code.append(identifier)
            else:
                errors.append("wrong_socket")
        return {"code": code, "error":errors}
        
        