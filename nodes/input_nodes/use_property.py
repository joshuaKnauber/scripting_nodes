import bpy
from ..base_node import SN_ScriptingBaseNode
from ..node_looks import node_colors, node_icons
from ..node_utility import register_dynamic_input, get_input_value
from ...node_sockets import update_socket_autocompile


class SN_UseSearchPropertyGroup(bpy.types.PropertyGroup):

    name: bpy.props.StringProperty(name="Name", default="")
    identifier: bpy.props.StringProperty(name="Identifier",default="")

class SN_GetPropertiesNode(bpy.types.Node, SN_ScriptingBaseNode):
    '''Node to get the value of a properties'''
    bl_idname = 'SN_GetPropertiesNode'
    bl_label = "Get Property"
    bl_icon = node_icons["INPUT"]

    sn_use_property_properties: bpy.props.CollectionProperty(type=SN_UseSearchPropertyGroup)
    propName: bpy.props.StringProperty(name="Name", description="Compile to see your custom properties", default="", update=update_socket_autocompile)

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["INPUT"]

        inp = self.inputs.new('SN_SceneDataSocket', "Scene Data")
        inp.display_shape = "SQUARE"
        self.outputs.new('SN_DataSocket', "Output")

    def update(self):
        if len(self.inputs) > 0:
            self.sn_use_property_properties.clear()
            if len(self.inputs[0].links) == 1:
                if self.inputs[0].links[0].from_socket.bl_idname == "SN_SceneDataSocket":
                    value = ("").join(self.inputs[0].links[0].from_node.internal_evaluate(self.inputs[0].links[0].from_socket)["code"])

                    for prop in dir(eval(value)):
                        if prop[0] != "_":
                            item = self.sn_use_property_properties.add()
                            item.identifier = prop
                            item.name = prop.replace("_", " ").title()


    def copy(self, node):
        pass# called when node is copied

    def free(self):
        pass# called when node is removed

    def draw_buttons(self, context, layout):
        layout.prop_search(self, "propName", self, "sn_use_property_properties", text="")

    def evaluate(self,output):
        errors = []
        code = []

        if len(self.inputs) > 0:
            if len(self.inputs[0].links) == 1:
                if self.inputs[0].links[0].from_socket.bl_idname == "SN_SceneDataSocket":
                    code.append(("").join(self.inputs[0].links[0].from_node.internal_evaluate(self.inputs[0].links[0].from_socket)["code"]))
                else:
                    errors.append("wrong_socket")
            else:
                errors.append("no_connection")
        if len(errors) == 0:
            if self.propName in self.sn_use_property_properties:
                code.append(".")
                code.append(self.sn_use_property_properties[self.propName].identifier)
            else:
                errors.append("invalid_prop")
        else:
            code.append("''")


        return {"code": code, "error":errors}

