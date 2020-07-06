import bpy
from ..base.base_node import SN_ScriptingBaseNode
from ...compile.compiler import compiler
from ..base.node_looks import node_colors, node_icons
from ...handler.custom_properties import CustomProperties

class SN_LayoutSearchPropertyGroup(bpy.types.PropertyGroup):

    name: bpy.props.StringProperty(default="")
    identifier: bpy.props.StringProperty(default="")
    isEnum: bpy.props.BoolProperty(default=False)
    isBool: bpy.props.BoolProperty(default=False)
    isCustom: bpy.props.BoolProperty(default=False)

class SN_ForLayoutNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_ForLayoutNode"
    bl_label = "For (Layout)"
    bl_icon = node_icons["PROGRAM"]
    _should_be_registered = False

    CustomProperties = CustomProperties()

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'ScriptingNodesTree'

    def socket_update(self, context):
        compiler().socket_update()

    def get_var_name(self):
        highest_var_name = 0
        for node in bpy.context.space_data.node_tree.nodes:
            if node.bl_idname == self.bl_idname:
                number = int(node.var_name.split("_")[-1])
                highest_var_name = max(number,highest_var_name)
        return "forLayoutNode_"+str(highest_var_name + 1)

    def update_prop_name(self, context):
        self.socket_update(context)
        self.inputs["Name"].value = self.propName

    def update(self):
        if len(self.inputs) == 2:
            self.sn_layout_property_properties.clear()
            if len(self.inputs[0].links) >= 1:
                self.test_collection()
                
                if self.is_collection:
                    code = self.inputs[0].links[0].from_node.data_type(self.inputs[0].links[0].from_socket)
                    if code != "":
                        if "bl_rna.properties" in code:
                            code+=".fixed_type"
                            code="bpy.types." + eval("type("+code+").bl_rna.identifier")
                        elif "bpy.data." in code:
                            code = code.split(".")[-1]
                            code = "bpy.data.bl_rna.properties['" + code + "']"
                            code = "bpy.types." + eval("type(" + code + ".fixed_type)").bl_rna.identifier
                        
                        for prop in eval(code).bl_rna.properties:
                            if prop.name != "RNA" and not "bl_" in prop.name:
                                item = self.sn_layout_property_properties.add()
                                item.name = prop.name
                                item.identifier = prop.identifier
                                if eval(code+".bl_rna.properties['"+prop.identifier+"'].type") == "ENUM":
                                    item.isEnum = True
                                elif eval(code+".bl_rna.properties['"+prop.identifier+"'].type") == "BOOLEAN":
                                    item.isBool = True
                        
                        self.CustomProperties.handle_layout_property(self, code.split(".")[-1])

    sn_layout_property_properties: bpy.props.CollectionProperty(type=SN_LayoutSearchPropertyGroup)
    propName: bpy.props.StringProperty(name="Name", description="The name of the property", update=update_prop_name)
    propEmboss: bpy.props.BoolProperty(name="Emboss", description="The property gets embossed", default=True, update=socket_update)
    propExpand: bpy.props.BoolProperty(name="Expand", description="The enum gets expanded", default=False, update=socket_update)
    propToggle: bpy.props.BoolProperty(name="Toggle", description="The boolean gets expanded", default=False, update=socket_update)
    var_name: bpy.props.StringProperty(default="forLayoutNode_0")
    is_collection: bpy.props.BoolProperty()

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["INTERFACE"]

        self.inputs.new('SN_SceneDataSocket', "Scene Data").display_shape = "SQUARE"
        self.inputs.new('SN_StringSocket', "Name")
        self.outputs.new('SN_LayoutSocket', "Layout")

    def draw_buttons(self, context, layout):
        self.draw_icon_chooser(layout)
        layout.prop_search(self, "propName", self, "sn_layout_property_properties", text="")
        if self.propName in self.sn_layout_property_properties:
            layout.prop(self, "propEmboss")
            if self.sn_layout_property_properties[self.propName].isEnum:
                layout.prop(self, "propExpand")
            elif self.sn_layout_property_properties[self.propName].isBool:
                layout.prop(self, "propToggle")

    def copy(self, node):
        self.var_name = self.get_var_name()

    def test_collection(self):
        if len(self.inputs[0].links) > 0:
            if self.inputs[0].links[0].from_node.bl_idname == "SN_SceneData":
                self.is_collection = True
            elif self.inputs[0].links[0].from_socket.bl_idname == "SN_SceneDataSocket":
                code = self.inputs[0].links[0].from_node.data_type(self.inputs[0].links[0].from_socket)
                if code != "":
                    if "bl_rna.properties" in code:
                        if eval(code).type == "COLLECTION":
                            self.is_collection = True
                        else:
                            self.is_collection = False
                    else:
                        self.is_collection = False
                else:
                    self.is_collection = False
            else:
                self.is_collection = False

    def evaluate(self, output):
        self.test_collection()
        if self.propName in self.sn_layout_property_properties:
            error_list = []

            for_code, errors = self.SocketHandler.socket_value(self.inputs[0])
            error_list+=errors
            if not self.is_collection:
                for_code = ["["] + for_code + ["]"]

            layout_type, errors = self.SocketHandler.get_layout_type(self.outputs[0])
            error_list += errors

            text_input, errors = self.SocketHandler.socket_value(self.inputs[1])
            error_list += errors

            scene_data, errors = self.SocketHandler.socket_value(self.inputs[0])
            error_list += errors

            icon = []
            if self.icon:
                icon = [", icon=\""+self.icon+"\""]

            emboss = [", emboss="] + [str(self.propEmboss)]

            expand = []
            if self.sn_layout_property_properties[self.propName].isEnum:
                expand = [", expand="] + [str(self.propExpand)]
            
            toggle = []
            if self.sn_layout_property_properties[self.propName].isBool:
                toggle = [", toggle="] + [str(self.propToggle)]

            return {
                "blocks": [
                    {
                        "lines": [
                            [self.var_name + " = 0"],
                            ["for " + self.var_name + " in "] + scene_data + [":"]
                        ],
                        "indented": [
                            [layout_type,".prop(" + self.var_name + ", \"" + self.sn_layout_property_properties[self.propName].identifier + "\", text="] + text_input + expand + toggle + emboss + icon + [")"]
                        ]
                    }
                ],
                "errors": error_list
            }
        else:
            return {
                "blocks": [
                    {
                        "lines": [],
                        "indented": []
                    }
                ],
                "errors": []
        }

    def needed_imports(self):
        return []