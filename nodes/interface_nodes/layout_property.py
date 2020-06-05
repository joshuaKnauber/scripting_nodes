import bpy
from ..base_node import SN_ScriptingBaseNode
from ..node_looks import node_colors, node_icons
from ..node_utility import register_dynamic_input, get_input_value, get_types
from ...node_sockets import update_socket_autocompile


class SN_LayoutSearchPropertyGroup(bpy.types.PropertyGroup):

    name: bpy.props.StringProperty(name="Name", default="")
    identifier: bpy.props.StringProperty(name="Identifier",default="")

class SN_UiPropertiesNode(bpy.types.Node, SN_ScriptingBaseNode):
    '''Node to use a property in a panel'''
    bl_idname = 'SN_UiPropertiesNode'
    bl_label = "Layout Property"
    bl_icon = node_icons["INTERFACE"]

    sn_layout_property_properties: bpy.props.CollectionProperty(type=SN_LayoutSearchPropertyGroup)
    propName: bpy.props.StringProperty(name="Name", description="Compile to see your custom properties", default="", update=update_socket_autocompile)

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["INTERFACE"]

        inp = self.inputs.new('SN_SceneDataSocket', "Scene Data")
        inp.display_shape = "SQUARE"
        self.outputs.new('SN_LayoutSocket', "Layout")


    def update(self):
        if len(self.inputs) > 0:
            self.sn_layout_property_properties.clear()
            if len(self.inputs[0].links) == 1:
                if self.inputs[0].links[0].from_socket.bl_idname == "SN_SceneDataSocket":
                    value = ("").join(self.inputs[0].links[0].from_node.internal_evaluate(self.inputs[0].links[0].from_socket)["code"])

                    for prop in dir(eval(value)):
                        if prop[0] != "_":
                            item = self.sn_layout_property_properties.add()
                            item.identifier = prop
                            item.name = prop.replace("_", " ").title()

    def copy(self, node):
        pass# called when node is copied

    def free(self):
        pass# called when node is removed

    def draw_buttons(self, context, layout):
        layout.prop_search(self, "propName", self, "sn_layout_property_properties", text="")

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
            if self.propName in self.sn_layout_property_properties:
                code.append(", '")
                code.append(self.sn_layout_property_properties[self.propName].identifier)
                code = ["_INDENT__INDENT_", self.outputs[0].links[0].to_node.layout_type(),
                        ".prop("] + code + ["')\n"]
            else:
                errors.append("invalid_prop")
        else:
            code.append("''")

        return {"code":code, "error":errors}

