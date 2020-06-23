import bpy
from ..base.base_node import SN_ScriptingBaseNode
from ...compile.compiler import compiler
from ..base.node_looks import node_colors, node_icons
from ...handler.custom_properties import CustomProperties


class SN_ChangePropertySearchGroup(bpy.types.PropertyGroup):

    name: bpy.props.StringProperty(name="Name", default="")
    identifier: bpy.props.StringProperty(name="Identifier",default="")
    isCustom: bpy.props.BoolProperty(default=False)
    prop_type: bpy.props.StringProperty(default="")


class SN_ChangeProperty(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_ChangeProperty"
    bl_label = "Change Property"
    bl_icon = node_icons["PROGRAM"]

    CustomProperties = CustomProperties()

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'ScriptingNodesTree'

    def socket_update(self, context):
        compiler().socket_update()

    def propName_update(self, context):
        for inp in self.inputs:
            if inp.bl_idname != "SN_ProgramSocket" and inp.bl_idname != "SN_SceneDataSocket":
                self.inputs.remove(inp)
        
        if len(self.sn_change_property_properties) > 0 and self.propName != "":
            if self.sn_change_property_properties[self.propName].isCustom:
                self.inputs.new(self.sn_change_property_properties[self.propName].prop_type, self.propName)
            else:
                code = self.inputs[1].links[0].from_node.data_type(self.inputs[1].links[0].from_socket)
                if code != "":
                    if "bl_rna.properties" in code:
                        code+=".fixed_type"
                        code="bpy.types." + eval("type("+code+").bl_rna.identifier")
                    prop = eval(code + ".bl_rna.properties['" + self.sn_change_property_properties[self.propName].identifier + "']")
                    if prop.type == "STRING":
                        self.inputs.new("SN_StringSocket", self.propName)
                    elif prop.type == "FLOAT":
                        if prop.array_length > 0:
                            self.inputs.new("SN_VectorSocket", self.propName)
                        else:
                            self.inputs.new("SN_FloatSocket", self.propName)
                    elif prop.type == "INT":
                        if prop.array_length > 0:
                            self.inputs.new("SN_VectorSocket", self.propName)
                        else:
                            self.inputs.new("SN_IntSocket", self.propName)
                    elif prop.type == "BOOLEAN":
                        self.inputs.new("SN_BooleanSocket", self.propName)
                    elif prop.type == "ENUM":
                        self.inputs.new("SN_StringSocket", self.propName)
                    elif prop.type != "POINTER":
                        self.inputs.new("SN_DataSocket", self.propName)

        self.socket_update(context)


    sn_change_property_properties: bpy.props.CollectionProperty(type=SN_ChangePropertySearchGroup)
    propName: bpy.props.StringProperty(name="Name", description="The name of the property", update=propName_update)

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["PROGRAM"]

        self.inputs.new('SN_ProgramSocket', "Program").display_shape = "DIAMOND"
        self.inputs.new('SN_SceneDataSocket', "Scene Data").display_shape = "SQUARE"
        self.outputs.new('SN_ProgramSocket', "Program").display_shape = "DIAMOND"

    def draw_buttons(self, context, layout):
        layout.prop_search(self,"propName", self, "sn_change_property_properties")

    def update(self):
        self.sn_change_property_properties.clear()
        if len(self.inputs) > 1:
            if len(self.inputs[1].links) > 0:
                if self.inputs[1].links[0].from_socket.bl_idname == "SN_SceneDataSocket":
                    code = self.inputs[1].links[0].from_node.data_type(self.inputs[1].links[0].from_socket)
                    
                    if code != "":
                        if self.inputs[1].links[0].from_node.bl_idname == "SN_SceneData":
                            is_collection = True
                        else:
                            is_collection = False
                            if "bl_rna.properties" in code:
                                if eval(code + ".type") == "COLLECTION":
                                    is_collection = True
                            else:
                                is_collection = False

                        if not is_collection:
                            if "bl_rna.properties" in code:
                                code+=".fixed_type"
                            for prop in eval(code).bl_rna.properties:
                                if prop.name != "RNA" and not "bl_" in prop.name:
                                    if prop.is_readonly == False:
                                        item = self.sn_change_property_properties.add()
                                        item.name = prop.name
                                        item.identifier = prop.identifier
                            
                            self.CustomProperties.handle_change_property(self, code.split(".")[-1])


    def evaluate(self, output):
        errors = []
        propType, errors = self.SocketHandler.socket_value(self.inputs[1])
        if len(self.inputs) > 2:
            propValue, error = self.SocketHandler.socket_value(self.inputs[2])
            errors+=error
            if propValue == []:
                propValue = ["None"]
        else:
            propValue = ["None"]
            errors.append({"error": "no_prop_selected", "node": self})

        if self.propName == "":
            propName = "none"
            errors.append({"error": "no_prop_selected", "node": self})
        else:
            propName = self.sn_change_property_properties[self.propName].identifier

        continue_code, error = self.SocketHandler.socket_value(self.outputs[0], False)
        errors+=error
        
        return {
            "blocks": [
                {
                    "lines": [
                        propType + ["." +  propName + " = "] + propValue,
                    ],
                    "indented": [
                    ]
                },
                {
                    "lines": [
                        continue_code
                    ],
                    "indented": [
                    ]
                }
            ],
            "errors": errors
        }

    def needed_imports(self):
        return []