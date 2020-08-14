#SN_EnumSelectorLayoutNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_EnumSearchPropertyGroup(bpy.types.PropertyGroup):

    name: bpy.props.StringProperty(default="")
    identifier: bpy.props.StringProperty(default="")
    description: bpy.props.StringProperty(default="")

class SN_EnumSelectorLayoutNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_EnumSelectorLayoutNode"
    bl_label = "Enum Selector (Layout)"
    bl_icon = "CON_ACTION"
    node_color = (0.89,0.6,0)
    should_be_registered = False

    def reset_data_type(self, context):
        if self.inputs[1].links[0].from_socket.bl_idname == "SN_ObjectSocket":
            self.update()

    def update_name(self, context):
        for out in self.outputs:
            if out.name != "Layout":
                try:
                    self.outputs.remove(out)
                except RuntimeError:
                    pass 
        self.generate_sockets()

    def update(self):
        self.sn_enum_property_properties.clear()

        if len(self.inputs) == 2:
            if len(self.inputs[1].links) == 1:
                if self.inputs[1].links[0].from_socket.bl_idname == "SN_ObjectSocket":

                    data_type = self.inputs[1].links[0].from_node.data_type(self.inputs[1].links[0].from_socket)
                    if data_type != "":
                        for prop in eval(data_type).bl_rna.properties:
                            if prop.type == "ENUM":
                                item = self.sn_enum_property_properties.add()
                                item.name = prop.name
                                item.identifier = prop.identifier
                                item.description = prop.description
        
        if not self.propName in self.sn_enum_property_properties:
            self.propName = ""

    def generate_sockets(self):
        if self.propName in self.sn_enum_property_properties:
            data_type = self.inputs[1].links[0].from_node.data_type(self.inputs[1].links[0].from_socket)
            if data_type != "":
                for item in eval(data_type + ".bl_rna.properties['" + self.sn_enum_property_properties[self.propName].identifier + "'].enum_items"):
                    self.sockets.create_output(self,"LAYOUT", item.name)

    propName: bpy.props.StringProperty(name="Name", description="The name of the property", update=update_name)
    sn_enum_property_properties: bpy.props.CollectionProperty(type=SN_EnumSearchPropertyGroup)

    def inititialize(self,context):
        self.sockets.create_input(self,"LAYOUT","Layout")
        self.sockets.create_input(self,"OBJECT","Input")

    def draw_buttons(self, context, layout):
        layout.prop_search(self,"propName",self,"sn_enum_property_properties",text="")

    def evaluate(self, socket, input_data, errors):
        return {
            "blocks": [
                {
                    "lines": [ # lines is a list of lists, where the lists represent the different lines
                    ],
                    "indented": [ # indented is a list of lists, where the lists represent the different lines
                    ]
                }
            ],
            "errors": []
        }

