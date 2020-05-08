import bpy
from ...node_sockets import update_socket_autocompile
from ..base_node import SN_ScriptingBaseNode
from ..node_looks import node_colors, node_icons
from .scene_nodes_utils import add_data_output


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

    def generate_sockets(self):
        if self.inputs[0].is_linked:
            if self.inputs[0].links[0].from_socket.bl_idname == "SN_SceneDataSocket":

                if self.previous_connection != self.inputs[0].links[0].from_socket.name:
                    self.previous_connection = self.inputs[0].links[0].from_socket.name
                    for socket in self.outputs:
                        self.outputs.remove(socket)

                    code = ("").join(self.inputs[0].links[0].from_node.evaluate(self.inputs[0].links[0].from_socket)["code"])
                    data_block = None
                    if len(eval(code)) == 0:
                        data_block = eval(code+".new(name='sn_temp_data_block')")

                    ignore_props = ["RNA","Full Name","Is Evaluated","Original ID","Embedded Data","Tag",
                                    "Is Indirect","Library","Library Override","Preview","Data","Bounding Box",
                                    "Parent Vertices","Proxy","Proxy Collection","Delta Location",
                                    "Delta Rotation (Euler)","Delta Rotation (Quaternion)","Delta Scale",
                                    "Matrix World","Local Matrix","Input Matrix","Parent Inverse Matrix",
                                    "Image User","Empty Image Depth","Display in Perspective Mode",
                                    "Display in Orthographic Mode","Display Only Axis Aligned","Empty Image Side",
                                    ]
                    for prop in eval(code+"[0]"+".bl_rna.properties"):
                        if not prop.name in ignore_props:
                            add_data_output(self,prop,prop.name)

                    if data_block:
                        eval(code+".remove("+code+"[0])")
        else:
            for socket in self.outputs:
                self.outputs.remove(socket)

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
        return {"code": []}
        
        