import bpy
from ..base.base_node import SN_ScriptingBaseNode
from ...compile.compiler import compiler
from ..base.node_looks import node_colors, node_icons
from ...handler.data_block_handler import DataBlockHandler


class SN_CreateDataBlock(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_CreateDataBlock"
    bl_label = "Create Data Block"
    bl_icon = node_icons["OPERATOR"]
    bl_width_default = 275

    DataBlock = DataBlockHandler()

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'ScriptingNodesTree'

    def socket_update(self, context):
        compiler().socket_update()

    def updateLoc(self, context):
        self.generate_sockets()
        self.socket_update(context)

    def get_socket_items(self, context):
        data = self.DataBlock.get_data_blocks()[self.propLocation]
        for socket in data:
            if socket[0] == "SN_EnumSocket":
                return socket[2]

    def generate_sockets(self):
        if self.propLocation != "":
            self.DataBlock.generate_sockets(self)

    def getItems(self, context):
        items = []

        for obj in dir(bpy.data):
            if "new" in eval("dir(bpy.data."+obj+")"):
                if obj != "objects":
                    items.append((obj, eval("bpy.data."+obj+".bl_rna.name").replace("Main ", ""), eval("bpy.data."+obj+".bl_rna.description")))

        return items

    def get_var_name(self):
        highest_var_name = 0
        for node in bpy.context.space_data.node_tree.nodes:
            if node.bl_idname == self.bl_idname:
                number = int(node.var_name.split("_")[-1])
                highest_var_name = max(number,highest_var_name)
        return "data_var_"+str(highest_var_name + 1)

    propLocation: bpy.props.EnumProperty(items=getItems, name="Location", description="Location of the data", update=updateLoc)
    var_name: bpy.props.StringProperty(default="data_var_0")

    def init(self, context):
        self.var_name = self.get_var_name()
        self.use_custom_color = True
        self.color = node_colors["OPERATOR"]

        self.inputs.new("SN_ProgramSocket", "Program").display_shape = "DIAMOND"
        self.inputs.new("SN_StringSocket", "Name")
        self.outputs.new("SN_ProgramSocket", "Program").display_shape = "DIAMOND"
        self.outputs.new("SN_SceneDataSocket", "Scene Data").display_shape = "SQUARE"

    def draw_buttons(self, context, layout):
        layout.prop(self,"propLocation")

    def evaluate(self, output):
        if output == self.outputs[-1]:
            return {
                "blocks": [
                    {
                        "lines": [
                            [self.var_name]
                        ],
                        "indented": []
                    }
                ],
                "errors": []
            }

        continue_code, errors = self.SocketHandler.socket_value(self.outputs[0], False)
        name, error = self.SocketHandler.socket_value(self.inputs[1])
        errors+=error

        image_props = {"Alpha": "alpha","Float Buffer": "float_buffer","Stereo 3D": "stereo3d","Is Data": "is_data","Tiled": "tiled"}

        inputs = []
        for inp in self.inputs:
            if inp.bl_idname != "SN_ProgramSocket":
                if self.propLocation != "images":
                    inp, error = self.SocketHandler.socket_value(inp)
                    errors+=error
                    inp+=[", "]
                    inputs+=inp 
                else:
                    if inp.bl_idname != "SN_BooleanSocket":
                        inp, error = self.SocketHandler.socket_value(inp)
                        errors+=error
                        inp+=[", "]
                        inputs+=inp 
                    else:
                        inp_value, error = self.SocketHandler.socket_value(inp)
                        inp = [image_props[inp.name] + "="] + inp_value
                        errors+=error
                        inp+=[", "]
                        inputs+=inp 

        return {
            "blocks": [
                {
                    "lines": [
                        [self.var_name + " = bpy.data." + self.propLocation + ".new("] + inputs + [")"]
                    ],
                    "indented": []
                },
                {
                    "lines": [
                        continue_code
                    ],
                    "indented": []
                }
            ],
            "errors": errors
        }

    def data_type(self, output):
        return "bpy.types." + type(eval("bpy.data.bl_rna.properties[\""+ self.propLocation + "\"].fixed_type")).bl_rna.identifier

    def needed_imports(self):
        return ["bpy"]
