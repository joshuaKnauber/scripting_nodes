import bpy
from ..base_node import SN_ScriptingBaseNode
from ..node_looks import node_colors, node_icons
from ...node_sockets import update_socket_autocompile


class SN_EnumItemPropertyGroup(bpy.types.PropertyGroup):

    identifier: bpy.props.StringProperty(name="Identifier", default="")
    name: bpy.props.StringProperty(name="Name", default="")
    description: bpy.props.StringProperty(name="Description", default="")
    socket: bpy.props.StringProperty(name="Description", default="")


class SN_UseOperatorNode(SN_ScriptingBaseNode):
    '''Node for using an existing operator'''

    bl_width_default = 220

    socket_list: bpy.props.CollectionProperty(type=SN_EnumItemPropertyGroup)

    def op_items(self):
        for item in bpy.context.scene.sn_op_type_properties:
            if item.isCustom:
                bpy.context.scene.sn_op_type_properties.remove(bpy.context.scene.sn_op_type_properties.find(item.name))
        

        if len(bpy.context.scene.sn_op_type_properties) == 0:
            bpy.context.scene.sn_op_type_properties.clear()
            for prop in dir(bpy.ops):
                for op in dir(eval("bpy.ops."+prop)):
                    name = eval("bpy.ops."+prop+"."+op+".get_rna_type().name")
                    found = False
                    for item in bpy.context.scene.sn_op_type_properties:
                        if item.name == name:
                            found = True
                    if not found and name != "" and name.replace("-","").lstrip() != "":
                        item = bpy.context.scene.sn_op_type_properties.add()
                        item.identifier = "bpy.ops."+prop+"."+op
                        item.description = eval("bpy.ops."+prop+"."+op+".get_rna_type().description")
                        item.name = name

        for node in bpy.context.space_data.node_tree.nodes:
            if node.bl_idname == "SN_OperatorNode":
                item = bpy.context.scene.sn_op_type_properties.add()

                name = node.operator_name.lower().replace(" ","_")
                item.identifier = "bpy.ops.sn." + name
                item.description = ""
                item.name = node.operator_name
                item.isCustom = True
        

    def update_type(self,context):
        update_socket_autocompile(self, context)
        self.op_items()

        if not self.opType == "":
            self.generate_sockets()
            for item in bpy.context.scene.sn_op_type_properties:
                if item.name == self.opType:
                    self.opDescription = item.description
        else:
            self.opDescription = ""

    def get_identifier(self):
        for item in bpy.context.scene.sn_op_type_properties:
            if item.name == self.opType:
                return item.identifier
    

    opType: bpy.props.StringProperty(name="Operator", description="Operator Type", update=update_type)
    opDescription: bpy.props.StringProperty(name="Description",description="Operator description")


    def generate_sockets(self):
        self.socket_list.clear()

        for inp in self.inputs:
            if not inp.bl_idname == "SN_ProgramSocket":
                self.inputs.remove(inp)

        ignore_attr = ["RNA"]

        if self.opType != "":
            opType = self.get_identifier()
            isCustom = False
            try:
                eval(opType+".get_rna_type()")
            except:
                isCustom = True
            if not isCustom:
                for prop in eval(opType+".get_rna_type().properties"):
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

                        inp = self.inputs.new(socket_type, prop.identifier.replace("_"," ").title())
                        if socket_type == "SN_EnumSocket":
                            for item in prop.enum_items:
                                prop_item = self.socket_list.add()
                                prop_item.socket = prop.name
                                prop_item.identifier = item.identifier
                                prop_item.name = item.name
                                prop_item.description = item.description

                        if socket_type != "SN_VectorSocket":
                            inp.value = prop.default
                        else:
                            inp.value = (prop.default, prop.default, prop.default)

    def get_socket_items(self,socket):
        items = []
        for item in self.socket_list:
            if item.socket == socket.identifier:
                items.append((item.identifier,item.name,item.description))
        return items

