import bpy
from ..base.base_node import SN_ScriptingBaseNode
from ...compile.compiler import compiler
from ..base.node_looks import node_colors, node_icons
from ...handler.custom_properties import CustomProperties


class SN_EnumSearchPropertyGroup(bpy.types.PropertyGroup):

    name: bpy.props.StringProperty(default="")
    identifier: bpy.props.StringProperty(default="")
    isCustom: bpy.props.BoolProperty(default=False)

class SN_EnumProgramNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_EnumProgramNode"
    bl_label = "Enum Selector (Program)"
    bl_icon = node_icons["PROGRAM"]
    _should_be_registered = False

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'ScriptingNodesTree'

    def socket_update(self, context):
        compiler().socket_update()

    def update_name(self, context):
        for out in self.outputs:
            if out.name != "Program":
                self.outputs.remove(out)
        self.generate_sockets()

    def generate_sockets(self):
        if self.propName in self.sn_enum_property_properties:
            code = self.inputs[1].links[0].from_node.data_type(self.inputs[1].links[0].from_socket)
            for item in eval(code + ".bl_rna.properties['" + self.sn_enum_property_properties[self.propName].identifier + "'].enum_items"):
                self.outputs.new("SN_ProgramSocket", item.name).display_shape = "DIAMOND"

    sn_enum_property_properties: bpy.props.CollectionProperty(type=SN_EnumSearchPropertyGroup)
    propName: bpy.props.StringProperty(name="Name", description="The name of the property", update=update_name)
    CustomProperties = CustomProperties()

    def update(self):
        if len(self.inputs) == 2:
            self.sn_enum_property_properties.clear()
            self.generate_sockets()
            if len(self.inputs[1].links) > 0:
                if self.inputs[1].links[0].from_node.bl_idname == "SN_SceneData":
                    is_collection = True
                elif self.inputs[1].links[0].from_socket.bl_idname == "SN_SceneDataSocket":
                    code = self.inputs[1].links[0].from_node.data_type(self.inputs[1].links[0].from_socket)

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
        self.color = node_colors["PROGRAM"]

        self.inputs.new('SN_ProgramSocket', "Program").display_shape = "DIAMOND"
        self.inputs.new('SN_SceneDataSocket', "Scene Data").display_shape = "SQUARE"

        self.outputs.new('SN_ProgramSocket', "Program").display_shape = "DIAMOND"

    def draw_buttons(self, context, layout):
        layout.prop_search(self, "propName", self, "sn_enum_property_properties", text="")

    def evaluate(self, output):
        continue_code, errors = self.SocketHandler.socket_value(self.outputs[0],False)
        scene_data, error = self.SocketHandler.socket_value(self.inputs[1])
        errors+=error

        outputs = []

        if self.propName in self.sn_enum_property_properties:
            code = self.inputs[1].links[0].from_node.data_type(self.inputs[1].links[0].from_socket)

            if len(self.outputs) > 1:
                for out in self.outputs:
                    if out != self.outputs[0]:
                        value, error = self.SocketHandler.socket_value(out,False)
                        errors+=error
                        if value != []:
                            for item in eval(code + ".bl_rna.properties['" + self.sn_enum_property_properties[self.propName].identifier + "'].enum_items"):
                                if item.name == out.name:
                                    outputs.append({"lines": [["if "] + scene_data + ["." + self.sn_enum_property_properties[self.propName].identifier + " == \"" + item.identifier + "\":"]],"indented": [value]})

        return {
            "blocks": 
                outputs +
                [{
                    "lines": [
                        continue_code
                    ],
                    "indented": []
                }],
            "errors": errors
        }


    def needed_imports(self):
        return []