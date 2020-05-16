import bpy
from ...node_sockets import update_socket_autocompile
from ..base_node import SN_ScriptingBaseNode
from ..node_looks import node_colors, node_icons
from .scene_nodes_utils import add_data_output, get_active_types


class SN_SceneDataNode(bpy.types.Node, SN_ScriptingBaseNode):
    '''Scene Data Node for outputing data from the scene'''
    bl_idname = 'SN_SceneDataNode'
    bl_label = "Scene Data"
    bl_icon = node_icons["SCENE"]

    def data_type_items(self,context):
        ignore_data = ["RNA"]
        items = []
        for d_type in bpy.data.rna_type.properties:
            if not d_type.name in ignore_data:
                items.append((d_type.identifier,d_type.name,d_type.description))
        return items

    def update_data_type(self,context):
        self.generate_sockets()

    data_type: bpy.props.EnumProperty(items=data_type_items,update=update_data_type)

    def generate_sockets(self):
        to_connect = None
        if len(self.outputs) > 0:
            if self.outputs[0].is_linked:
                to_connect = self.outputs[0].links[0].to_socket

        for socket in self.outputs:
            self.outputs.remove(socket)

        result = eval("bpy.data."+self.data_type)
        label = self.data_type.replace("_"," ").title()
        add_data_output(self, result, label)

        if self.data_type in get_active_types():
            out = self.outputs.new('SN_SceneDataSocket', "Active "+self.data_type.title()[:-1])
            out.display_shape = "SQUARE"

        if to_connect:
            if self.outputs[0].bl_idname == to_connect.bl_idname:
                bpy.context.space_data.node_tree.links.new(self.outputs[0],to_connect)

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["INPUT"]

        self.generate_sockets()

    def copy(self, node):
        pass# called when node is copied

    def free(self):
        pass# called when node is removed

    def draw_buttons(self, context, layout):
        layout.label(text="Data type")
        layout.prop(self,"data_type",text="")

    def evaluate(self, output):
        code = []
        if output == self.outputs[0]:
            code += ["bpy.data.",self.data_type]
        else:
            code += ["bpy.context.","active_",self.data_type[:-1]]
        return {"code": code}
        
        