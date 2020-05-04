import bpy
from ..base_node import SN_ScriptingBaseNode
from ..node_looks import node_colors, node_icons
from ...node_sockets import update_socket_autocompile


class SN_EnumItemPropertyGroup(bpy.types.PropertyGroup):

    identifier: bpy.props.StringProperty(name="Identifier", default="")
    name: bpy.props.StringProperty(name="Name", default="")
    description: bpy.props.StringProperty(name="Description", default="")
    socket: bpy.props.StringProperty(name="Description", default="")


class SN_OperatorRunNode(bpy.types.Node, SN_ScriptingBaseNode):
    '''Node for running an operator'''
    bl_idname = 'SN_OperatorRunNode'
    bl_label = "Run Operator"
    bl_icon = node_icons["OPERATOR"]

    socket_list: bpy.props.CollectionProperty(type=SN_EnumItemPropertyGroup)

    def op_items(self):
        bpy.context.scene.sn_op_type_properties.clear()
        for prop in dir(bpy.ops):
            item = bpy.context.scene.sn_op_type_properties.add()
            item.name = prop.replace("_"," ").title()

    def run_items(self):
        bpy.context.scene.sn_op_run_properties.clear()
        opType = self.opType.lower().replace(" ","_")
        if opType == "":
            opType = "empty_op"
        for prop in dir(eval("bpy.ops."+opType)):
            item = bpy.context.scene.sn_op_run_properties.add()
            item.name = prop.replace("_"," ").title()

    def update_type(self,context):
        self.update_items(context)
        opType = self.opType.lower().replace(" ","_")
        if opType == "":
            opType = "empty_op"
        opRun = self.opRun.lower().replace(" ","_")
        if opRun == "":
            opRun = "empty_op"
        if len(dir(eval("bpy.ops."+opType+"."+opRun))) == 0:
            self.opRun = ""

    def update_run(self,context):
        self.update_items(context)
        self.generate_sockets()

    def update_items(self,context):
        update_socket_autocompile(self, context)

        self.op_items()
        self.run_items()

    opType: bpy.props.StringProperty(name="Operator", description="Operator Type", update=update_type)

    opRun: bpy.props.StringProperty(name="Operator", description="Operator", update=update_run)


    def generate_sockets(self):
        self.socket_list.clear()

        for inp in self.inputs:
            self.inputs.remove(inp)

        pIn = self.inputs.new('SN_ProgramSocket', "Program")
        pIn.display_shape = "DIAMOND"

        opType = self.opType.lower().replace(" ","_")
        opRun = self.opRun.lower().replace(" ","_")

        if opType == "":
            opType = "empty_op"
        opRun = self.opRun.lower().replace(" ","_")
        if opRun == "":
            opRun = "empty_op"

        ignore_attr = ["RNA"]

        if len(dir(eval("bpy.ops."+opType))) != 0:
            for prop in eval("bpy.ops."+opType+"."+opRun+".get_rna_type().properties"):
                if not prop.name in ignore_attr:

                    socket_type = "SN_DataSocket"
                    if prop.rna_type.identifier == "StringProperty":
                        socket_type = "SN_StringSocket"
                    elif prop.rna_type.identifier == "EnumProperty":
                        socket_type = "SN_EnumSocket"
                    elif prop.rna_type.identifier == "FloatProperty" or prop.rna_type.identifier == "IntProperty":
                        if prop.is_array:
                            socket_type = "SN_VectorSocket"
                        else:
                            socket_type = "SN_NumberSocket"
                    elif prop.rna_type.identifier == "BoolProperty":
                        socket_type = "SN_BooleanSocket"

                    inp = self.inputs.new(socket_type,prop.name)
                    if socket_type == "SN_EnumSocket":
                        for item in prop.enum_items:
                            prop_item = self.socket_list.add()
                            prop_item.socket = prop.name
                            prop_item.identifier = item.identifier
                            prop_item.name = item.name
                            prop_item.description = item.description

    def get_socket_items(self,socket):
        items = []
        for item in self.socket_list:
            if item.socket == socket.identifier:
                items.append((item.identifier,item.name,item.description))
        return items

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["OPERATOR"]

        out = self.outputs.new('SN_ProgramSocket', "Program")
        out.display_shape = "DIAMOND"

        self.generate_sockets()
        self.op_items()

    def draw_buttons(self, context, layout):
        layout.prop_search(self,"opType",context.scene,"sn_op_type_properties",text="")
        if self.opType != "":
            layout.prop_search(self,"opRun",context.scene,"sn_op_run_properties",text="")

    def evaluate(self,output):
        return {"code": [""]}