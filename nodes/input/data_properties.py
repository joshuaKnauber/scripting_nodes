import bpy
from ..base.base_node import SN_ScriptingBaseNode
from ...compile.compiler import compiler
from ..base.node_looks import node_colors, node_icons
from ...properties.groups.scene_data_properties import SN_SearchPropertyGroup
from ...handler.custom_properties import CustomProperties


class SN_DataProperties(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_DataProperties"
    bl_label = "Scene Data Properties"
    bl_icon = node_icons["SCENE"]

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'ScriptingNodesTree'

    def socket_update(self, context):
        compiler().socket_update()

    def update_use_index(self,context):
        self.inputs["Name"].hide = self.use_index
        self.inputs["Index"].hide = not self.use_index

        self.socket_update(context)

    def generate_sockets(self):
        if len(self.inputs) > 1 and len(self.outputs) > 1:
            if len(self.inputs[0].links) > 0:
                self.search_properties.clear()
                code = ""
                if self.inputs[0].links[0].from_node.bl_idname == "SN_SceneData":
                    self.is_collection = True
                elif self.inputs[0].links[0].from_socket.bl_idname == "SN_SceneDataSocket":
                    code = self.inputs[0].links[0].from_node.data_type(self.inputs[0].links[0].from_socket)

                    if code != "":
                        self.is_collection = False
                        if "bl_rna.properties" in code:
                            if eval(code + ".type") == "COLLECTION":
                                self.is_collection = True
                    else:
                        self.is_collection = False
                
                if self.is_collection:
                    self.inputs["Name"].hide = self.use_index
                    self.inputs["Index"].hide = not self.use_index
                    self.outputs["Element"].hide = False
                    self.outputs["Amount"].hide = False
                else:
                    self.inputs["Name"].hide = True
                    self.inputs["Index"].hide = True
                    self.outputs["Element"].hide = True
                    self.outputs["Amount"].hide = True
                    if code != "":
                        if "bl_rna.properties" in code:
                            code+=".fixed_type"
                            code="bpy.types." + eval("type("+code+").bl_rna.identifier")
                        for prop in eval(code).bl_rna.properties:
                            if prop.name != "RNA" and not "bl_" in prop.name:
                                item = self.search_properties.add()
                                item.name = prop.name
                                item.identifier = prop.identifier
                                item.description = prop.description
                                item.type = str(type(prop))

                        self.CustomProperties.handle_data_properties(self, code.split(".")[-1])

            else:
                self.is_collection = False
                self.inputs["Name"].hide = True
                self.inputs["Index"].hide = True
                self.outputs["Element"].hide = True
                self.outputs["Amount"].hide = True
                

    search_value: bpy.props.StringProperty(name="Search value", description="", update=socket_update)
    search_properties: bpy.props.CollectionProperty(type=SN_SearchPropertyGroup)
    use_index: bpy.props.BoolProperty(default=True, name="Use index", description="Use an index instead of a name to get the element", update=update_use_index)
    is_collection: bpy.props.BoolProperty(default=False)
    CustomProperties = CustomProperties()

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["SCENE"]

        self.inputs.new('SN_SceneDataSocket', "Scene Data").display_shape = "SQUARE"

        self.inputs.new("SN_IntSocket", "Index").hide = True
        self.inputs.new("SN_StringSocket", "Name").hide = True
        out = self.outputs.new("SN_SceneDataSocket", "Element")
        out.display_shape = "SQUARE"
        out.hide = True
        self.outputs.new("SN_IntSocket", "Amount").hide = True

        self.generate_sockets()

    def draw_buttons(self, context, layout):
        if not self.is_collection:
            row = layout.row(align=True)
            row.prop_search(self,"search_value",self,"search_properties",text="")

            has_output = False
            for out in self.outputs:
                if out.name == self.search_value:
                    has_output = True

            if not has_output and not self.search_value == "":
                op = row.operator("scripting_nodes.add_scene_data_socket",text="",icon="ADD")
                op.node_name = self.name
                op.socket_name = self.search_value
            if has_output:
                op = row.operator("scripting_nodes.remove_scene_data_socket",text="",icon="REMOVE")
                op.node_name = self.name
                op.socket_name = self.search_value
        else:
            layout.prop(self, "use_index")

    def copy(self, node):
        for out in self.outputs:
            if out.name != "Element" and out.name != "Amount":
                self.outputs.remove(out)
        self.search_value = ""
        self.search_properties.clear()
        self.generate_sockets()
    
    def update(self):
        if len(self.inputs[0].links) == 0:
            for out in self.outputs:
                if out.name != "Element" and out.name != "Amount":
                    self.outputs.remove(out)
        self.search_value = ""
        self.generate_sockets()

    def evaluate(self, output):
        errors = []
        if self.is_collection:
            if output == self.outputs[1]:
                collection, error = self.SocketHandler.socket_value(self.inputs[0])
                errors+=error
                return {
                    "blocks": [
                        {
                            "lines": [
                                ["len("] + collection + [")"]
                            ],
                            "indented": [
                            ]
                        }
                    ],
                    "errors": errors
                }
            else:
                collection, error = self.SocketHandler.socket_value(self.inputs[0])
                errors+=error
                if self.use_index:
                    index, error = self.SocketHandler.socket_value(self.inputs[1])
                    errors+=error
                else:
                    index, error = self.SocketHandler.socket_value(self.inputs[2])
                    errors+=error
                return {
                    "blocks": [
                        {
                            "lines": [
                                collection + ["["] + index + ["]"]
                            ],
                            "indented": [
                            ]
                        }
                    ],
                    "errors": errors
                }
        else:
            collection, error = self.SocketHandler.socket_value(self.inputs[0])
            errors+=error
            return {
                "blocks": [
                    {
                        "lines": [
                            collection + ["." + self.search_properties[output.name].identifier]
                        ],
                        "indented": [
                        ]
                    }
                ],
                "errors": errors
            }

    def data_type(self, output):
        if len(self.inputs[0].links) > 0:
            code = str(self.inputs[0].links[0].from_node.data_type(self.inputs[0].links[0].from_socket))
            if self.is_collection:
                if "bpy.data" in code:
                    code = code.split(".")[-1]
                    code = "bpy.data.bl_rna.properties['" + code + "']"
                return "bpy.types." + eval("type(" + code + ".fixed_type)").bl_rna.identifier
            else:
                if "bl_rna.properties" in code:
                    code = eval(code + ".fixed_type").bl_rna.identifier
                    code = "bpy.types." + code
                return code + ".bl_rna.properties['" + self.search_properties[output.name].identifier + "']"
        return ""

    def needed_imports(self):
        return ["bpy"]