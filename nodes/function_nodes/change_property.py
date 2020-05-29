import bpy
from ..base_node import SN_ScriptingBaseNode
from ..node_looks import node_colors, node_icons
from ..node_utility import register_dynamic_input, get_input_value, get_types
from ...node_sockets import update_socket_autocompile


class SN_ChangeSearchPropertyGroup(bpy.types.PropertyGroup):

    name: bpy.props.StringProperty(name="Name", default="")
    identifier: bpy.props.StringProperty(name="Identifier",default="")

class SN_SetPropertiesNode(bpy.types.Node, SN_ScriptingBaseNode):
    '''Node to get the value of a properties'''
    bl_idname = 'SN_SetPropertiesNode'
    bl_label = "Change Property"
    bl_icon = node_icons["OPERATOR"]

    sn_change_property_properties: bpy.props.CollectionProperty(type=SN_ChangeSearchPropertyGroup)
    propName: bpy.props.StringProperty(name="Name", description="Compile to see your custom properties", default="", update=update_socket_autocompile)

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["OPERATOR"]

        pIn = self.inputs.new('SN_ProgramSocket', "Program")
        pIn.display_shape = "DIAMOND"
        self.inputs.new('SN_DataSocket', "Value")
        inp = self.inputs.new('SN_SceneDataSocket', "Scene Data")
        inp.display_shape = "SQUARE"
        pOut = self.outputs.new('SN_ProgramSocket', "Program")
        pOut.display_shape = "DIAMOND"

    def update(self):
        if len(self.inputs) > 0:
            self.sn_change_property_properties.clear()
            if len(self.inputs[2].links) == 1:
                if self.inputs[2].links[0].from_socket.bl_idname == "SN_SceneDataSocket":
                    value = ("").join(self.inputs[2].links[0].from_node.internal_evaluate(self.inputs[2].links[0].from_socket)["code"])

                    for prop in dir(eval(value)):
                        if prop[0] != "_":
                            item = self.sn_change_property_properties.add()
                            item.identifier = prop
                            item.name = prop.replace("_", " ").title()

    def copy(self, node):
        pass# called when node is copied

    def free(self):
        pass# called when node is removed

    def draw_buttons(self, context, layout):
        layout.prop_search(self, "propName", self, "sn_change_property_properties", text="")

    def evaluate(self,output):
        errors = []
        code = []

        code.append(self.inputs[2].links[0].from_socket)
        code.append(".")
        code.append(self.sn_change_property_properties[self.propName].identifier)
        code.append(" = ")
        if not self.inputs[1].is_linked:
            errors.append("no_connection")
            code=["\n"]
            return {"code": code, "error": errors}
        else:
            return {"code": code+ [self.inputs[1].links[0].from_socket, "\n"]}
