import bpy
from ..base.base_node import SN_ScriptingBaseNode
from ...compile.compiler import compiler
from ..base.node_looks import node_colors, node_icons
from ...handler.custom_properties import CustomProperties


class SN_EnumSearchPropertyGroup(bpy.types.PropertyGroup):

    name: bpy.props.StringProperty(default="")
    identifier: bpy.props.StringProperty(default="")
    isCustom: bpy.props.BoolProperty(default=False)

class SN_EnumLayoutNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_EnumLayoutNode"
    bl_label = "Enum Selector (Layout)"
    bl_icon = node_icons["INTERFACE"]
    _should_be_registered = False

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'ScriptingNodesTree'

    def socket_update(self, context):
        compiler().socket_update()

    def update_name(self, context):
        for inp in self.inputs:
            if inp.name != "Scene Data":
                self.inputs.remove(inp)
        self.generate_sockets()

    def generate_sockets(self):
        if self.propName in self.sn_enum_property_properties:
            code = self.inputs[0].links[0].from_node.data_type(self.inputs[0].links[0].from_socket)
            for item in eval(code + ".bl_rna.properties['" + self.sn_enum_property_properties[self.propName].identifier + "'].enum_items"):
                self.inputs.new("SN_LayoutSocket", item.name)

    sn_enum_property_properties: bpy.props.CollectionProperty(type=SN_EnumSearchPropertyGroup)
    propName: bpy.props.StringProperty(name="Name", description="The name of the property", update=update_name)
    CustomProperties = CustomProperties()

    def update(self):
        if len(self.inputs) >= 1:
            self.sn_enum_property_properties.clear()
            self.generate_sockets()
            if len(self.inputs[0].links) > 0:
                if self.inputs[0].links[0].from_node.bl_idname == "SN_SceneData":
                    is_collection = True
                elif self.inputs[0].links[0].from_socket.bl_idname == "SN_SceneDataSocket":
                    code = self.inputs[0].links[0].from_node.data_type(self.inputs[0].links[0].from_socket)

                    if code != "":
                        is_collection = False
                        if "bl_rna.properties" in code:
                            if eval(code + ".type") == "COLLECTION":
                                is_collection = True
                    else:
                        is_collection = False
                else:
                    is_collection = True
                
                if not is_collection:
                    if code != "":
                        if "bl_rna.properties" in code:
                            code+=".fixed_type"
                            code="bpy.types." + eval("type("+code+").bl_rna.identifier")
                        for prop in eval(code).bl_rna.properties:
                            if eval(code+".bl_rna.properties['"+prop.identifier+"'].type") == "ENUM":
                                item = self.sn_enum_property_properties.add()
                                item.name = prop.name
                                item.identifier = prop.identifier

                        self.CustomProperties.handle_enum_property(self, code.split(".")[-1])

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["INTERFACE"]

        self.inputs.new('SN_SceneDataSocket', "Scene Data").display_shape = "SQUARE"

        self.outputs.new("SN_LayoutSocket", "Layout")

    def draw_buttons(self, context, layout):
        layout.prop_search(self, "propName", self, "sn_enum_property_properties", text="")

    def evaluate(self, output):
        scene_data, errors = self.SocketHandler.socket_value(self.inputs[0])
        inputs = []

        if self.propName in self.sn_enum_property_properties:
            code = self.inputs[0].links[0].from_node.data_type(self.inputs[0].links[0].from_socket)

            if len(self.inputs) > 1:
                for inp in self.inputs:
                    if inp != self.inputs[0]:
                        value, error = self.SocketHandler.socket_value(inp,False)
                        errors+=error
                        if value != []:
                            for item in eval(code + ".bl_rna.properties['" + self.sn_enum_property_properties[self.propName].identifier + "'].enum_items"):
                                if item.name == inp.name:
                                    inputs.append({"lines": [["if "] + scene_data + ["." + self.sn_enum_property_properties[self.propName].identifier + " == \"" + item.identifier + "\":"]],"indented": [value]})

        return {
            "blocks": inputs,
            "errors": errors
        }

    def layout_type(self):
        if self.outputs[0].is_linked:
            if self.outputs[0].links[0].to_socket.bl_idname == "SN_LayoutSocket":
                return self.outputs[0].links[0].to_node.layout_type()
        return "layout"

    def needed_imports(self):
        return []