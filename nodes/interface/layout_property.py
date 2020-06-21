import bpy
from ..base.base_node import SN_ScriptingBaseNode
from ...compile.compiler import compiler
from ..base.node_looks import node_colors, node_icons


class SN_LayoutSearchPropertyGroup(bpy.types.PropertyGroup):

    name: bpy.props.StringProperty(default="")
    identifier: bpy.props.StringProperty(default="")
    isEnum: bpy.props.BoolProperty(default=False)

class SN_LayoutProperty(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_LayoutProperty"
    bl_label = "Layout Property"
    bl_icon = node_icons["INTERFACE"]

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'ScriptingNodesTree'

    def socket_update(self, context):
        compiler().socket_update()

    def update(self):
        if len(self.inputs) == 2:
            self.sn_layout_property_properties.clear()
            if len(self.inputs[0].links) >= 1:
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
                
                if not is_collection:
                    if code != "":
                        if "bl_rna.properties" in code:
                            code+=".fixed_type"
                            code="bpy.types." + eval("type("+code+").bl_rna.identifier")
                        for prop in eval(code).bl_rna.properties:
                            if prop.name != "RNA" and not "bl_" in prop.name:
                                item = self.sn_layout_property_properties.add()
                                item.name = prop.name
                                item.identifier = prop.identifier
                                if eval(code+".bl_rna.properties['"+prop.identifier+"'].type") == "COLLECTION":
                                    item.isEnum = True


    sn_layout_property_properties: bpy.props.CollectionProperty(type=SN_LayoutSearchPropertyGroup)
    propName: bpy.props.StringProperty(name="Name", description="The name of the property", update=socket_update)
    propExpand: bpy.props.BoolProperty(name="Expand", description="The enum gets expanded", default=False, update=socket_update)

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
            if self.sn_layout_property_properties[self.propName].isEnum:
                layout.prop(self, "propExpand")

    def evaluate(self, output):
        if self.propName in self.sn_layout_property_properties:
            error_list = []

            layout_type, errors = self.SocketHandler.get_layout_type(self.outputs[0])
            error_list += errors

            text_input, errors = self.SocketHandler.socket_value(self.inputs[1])
            error_list += errors

            scene_data, errors = self.SocketHandler.socket_value(self.inputs[0])
            error_list += errors

            icon = []
            if self.icon:
                icon = [", icon=\""+self.icon+"\""]

            expand = []
            if self.sn_layout_property_properties[self.propName].isEnum:
                expand = [", expand="] + [str(self.propExpand)]

            return {
                "blocks": [
                    {
                        "lines": [
                            [layout_type,".prop("] + scene_data + [", \"" + self.sn_layout_property_properties[self.propName].identifier + "\", text="] + text_input + expand + icon + [")"]
                        ],
                        "indented": []
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
        return ["bpy"]