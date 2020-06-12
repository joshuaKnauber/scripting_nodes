import bpy
from ...node_sockets import update_socket_autocompile
from ..base_node import SN_ScriptingBaseNode
from ..node_looks import node_colors, node_icons
from .scene_nodes_utils import add_data_output, get_active_types, get_bpy_types
from ..node_utility import get_input_value
from ...properties.search_properties import SN_SearchPropertyGroup


class SN_DataPropertiesNode(bpy.types.Node, SN_ScriptingBaseNode):
    '''Scene Data Properties Node for outputting the properties of scene data'''
    bl_idname = 'SN_DataPropertiesNode'
    bl_label = "Scene Data Properties"
    bl_icon = node_icons["SCENE"]

    search_value: bpy.props.StringProperty(default="")

    search_properties: bpy.props.CollectionProperty(type=SN_SearchPropertyGroup)
    has_collection_input: bpy.props.BoolProperty(default=False)

    def update_use_index(self,context):
        update_socket_autocompile(self, context)

        self.inputs["Name"].hide = self.use_index
        self.inputs["Index"].hide = not self.use_index

    use_index: bpy.props.BoolProperty(default=False,name="Use index",description="Use an index instead of a name to get the element",update=update_use_index)

    def generate_sockets(self):
        if len(self.inputs[0].links) > 0:
            if self.inputs[0].links[0].from_socket.bl_idname == "SN_SceneDataSocket":

                self.search_properties.clear()

                code = ("").join(self.inputs[0].links[0].from_node.internal_evaluate(self.inputs[0].links[0].from_socket)["code"])

                if code != "":
                    self.has_collection_input = False
                    try:
                        if str(eval("type("+code+")")) == "<class 'bpy_prop_collection'>" or str(eval("type("+code+")")) == "<class 'bpy.types.CollectionProperty'>":
                            self.has_collection_input = True
                    except KeyError:
                        pass


                    if self.has_collection_input:
                        if len(self.outputs) != 2:
                            self.outputs.clear()
                            out = self.outputs.new('SN_SceneDataSocket', "Element")
                            out.display_shape = "SQUARE"

                            self.outputs.new('SN_IntSocket', "Amount")

                        self.inputs["Name"].hide = self.use_index
                        self.inputs["Index"].hide = not self.use_index

                    else:
                        for out in self.outputs:
                            if out.name == "Element" or out.name == "Amount":
                                self.outputs.remove(out)
                        self.inputs["Name"].hide = True
                        self.inputs["Index"].hide = True
                        ignore_props = ["RNA","Display Name","Full Name"]

                        for prop in eval(code+".bl_rna.properties"):
                            if not prop.name in ignore_props:
                                if not "bl_" in prop.name:
                                    item = self.search_properties.add()
                                    item.name = prop.name
                                    item.propType = str(type(prop))
        else:
            self.has_collection_input = False   
            self.outputs.clear()
            if len(self.inputs)  == 3:
                self.inputs["Name"].hide = True
                self.inputs["Index"].hide = True
            self.search_properties.clear()

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["INPUT"]

        inp = self.inputs.new('SN_SceneDataSocket', "Scene Data")
        inp.display_shape = "SQUARE"

        self.inputs.new("SN_IntSocket", "Index").hide = True
        self.inputs.new("SN_StringSocket", "Name").hide = True

        self.generate_sockets()

    def update(self):
        self.search_value = ""
        self.generate_sockets()

    def copy(self, node):
        self.search_value = ""
        self.search_properties.clear()
        self.has_collection_input = False
        self.generate_sockets()

    def free(self):
        pass# called when node is removed

    def draw_buttons(self, context, layout):
        if not self.has_collection_input:
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
            layout.prop(self,"use_index")

    def internal_evaluate(self, output):

        if self.has_collection_input:
            if output == self.outputs[0]:
                code = self.inputs[0].links[0].from_node.internal_evaluate(self.inputs[0].links[0].from_socket)["code"]
                if "bl_rna.properties" in code[0]:
                    code = eval("type("+code[0]+".fixed_type)").bl_rna.identifier
                    code = "bpy.types." + code
                    return {"code": code}
                else:
                    types = get_bpy_types()[code[-1]]
                    return {"code": ["bpy.types." + types]}
        else:
            code = ("").join(self.inputs[0].links[0].from_node.internal_evaluate(self.inputs[0].links[0].from_socket)["code"])
            for prop in eval(code+".bl_rna.properties"):
                if prop.name == output.name:
                    isCollection = False
                    try:
                        if str(eval("type("+code+".bl_rna.properties['"+prop.identifier+"'])")) == "<class 'bpy.types.CollectionProperty'>":
                            isCollection = True
                    except KeyError:
                        pass

                    if isCollection:
                        code+=".bl_rna.properties['"+prop.identifier+"']"
                    else:
                        code = eval("type("+code+".bl_rna.properties['" + prop.identifier + "'].fixed_type)").bl_rna.identifier
                        code = "bpy.types." + code
                    return{"code": [code]}

    def evaluate(self, output):
        errors = []

        if self.has_collection_input:
            if output == self.outputs[0]:
                if self.inputs[0].links[0].from_socket.bl_idname == "SN_SceneDataSocket":
                    code = "".join(self.inputs[0].links[0].from_node.internal_evaluate(self.inputs[0].links[0].from_socket)["code"])
                    for prop in eval(code+".bl_rna.properties"):
                        if prop.name == output.name:
                            code = "".join(self.inputs[0].links[0].from_node.evaluate(self.inputs[0].links[0].from_socket)["code"])
                            code+="." + prop.identifier

                else:
                    code = ""
                    errors.append("wrong_socket")
                
                return {"code": [code], "error": errors}
            else:
                if self.inputs[0].links[0].from_socket.bl_idname == "SN_SceneDataSocket":
                    code = "".join(self.inputs[0].links[0].from_node.internal_evaluate(self.inputs[0].links[0].from_socket)["code"])
                    for prop in eval(code+".bl_rna.properties"):
                        if prop.name == output.name:
                            code = "".join(self.inputs[0].links[0].from_node.evaluate(self.inputs[0].links[0].from_socket)["code"])
                            code+="." + prop.identifier
                else:
                    code = ""
                    errors.append("wrong_socket")
                
                return {"code": ["len(" + code + ")"], "error": errors}

        
        else:
            if self.inputs[0].links[0].from_socket.bl_idname == "SN_SceneDataSocket":
                code = "".join(self.inputs[0].links[0].from_node.internal_evaluate(self.inputs[0].links[0].from_socket)["code"])
                for prop in eval(code+".bl_rna.properties"):
                    if prop.name == output.name:
                        code = "".join(self.inputs[0].links[0].from_node.evaluate(self.inputs[0].links[0].from_socket)["code"])
                        code+="." + prop.identifier

            else:
                code = ""
                errors.append("wrong_socket")
            
            return {"code": [code], "error": errors}

