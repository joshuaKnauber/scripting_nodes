import bpy
from ...node_sockets import update_socket_autocompile
from ..base_node import SN_ScriptingBaseNode
from ..node_looks import node_colors, node_icons
from .scene_nodes_utils import add_data_output, get_active_types
from ..node_utility import get_types, get_input_value
from ...properties.search_properties import SN_SearchPropertyGroup


class SN_DataPropertiesNode(bpy.types.Node, SN_ScriptingBaseNode):
    '''Scene Data Properties Node for outputting the properties of scene data'''
    bl_idname = 'SN_DataPropertiesNode'
    bl_label = "Scene Data Properties"
    bl_icon = node_icons["SCENE"]

    previous_connection: bpy.props.StringProperty(default="")
    current_data_type: bpy.props.StringProperty(default="")
    search_value: bpy.props.StringProperty(default="")

    search_properties: bpy.props.CollectionProperty(type=SN_SearchPropertyGroup)
    has_collection_input: bpy.props.BoolProperty(default=False)

    def update_use_index(self,context):
        update_socket_autocompile(self, context)

        self.inputs["Index"].hide = not self.use_index
        self.inputs["Name"].hide = self.use_index

    use_index: bpy.props.BoolProperty(default=False,name="Use index",description="Use an index instead of a name to get the element",update=update_use_index)

    def get_data_name(self,name):
        if name.split("_")[0] == "active":
            active_types = get_active_types()
            for date in active_types:
                if active_types[date] == name.split("_")[-1]:
                    name = date
        return name

    def generate_sockets(self):
        if len(self.inputs[0].links) > 0:
            if self.inputs[0].links[0].from_socket.bl_idname == "SN_SceneDataSocket":

                if self.previous_connection != self.inputs[0].links[0].from_socket.name:

                    self.previous_connection = self.inputs[0].links[0].from_socket.name
                    self.outputs.clear()
                    for socket in self.inputs:
                        if not socket.bl_idname == "SN_SceneDataSocket":
                            self.inputs.remove(socket)
                    self.search_properties.clear()

                    code = ("").join(self.inputs[0].links[0].from_node.internal_evaluate(self.inputs[0].links[0].from_socket)["code"])
                    
                    is_collection = False
                    try:
                        if str(eval("type("+code+")")) == "<class 'bpy_prop_collection'>":
                            is_collection = True
                    except KeyError:
                        pass

                    if is_collection:
                        self.has_collection_input = True

                        out = self.outputs.new('SN_SceneDataSocket', "Element")
                        out.display_shape = "SQUARE"

                        self.outputs.new('SN_IntSocket', "Amount")

                        self.inputs.new('SN_IntSocket', "Index").hide = True
                        self.inputs.new('SN_StringSocket', "Name")

                    else:
                        self.has_collection_input = False

                        ignore_props = ["RNA","Display Name","Full Name"]

                        types = get_types()
                        data = self.get_data_name(code.split(".")[-1].split("[")[0])

                        for data_type in types:
                            if types[data_type] == data:
                                self.current_data_type = data_type
                                for prop in eval("bpy.types."+data_type+".bl_rna.properties"):
                                    if not prop.name in ignore_props:
                                        item = self.search_properties.add()
                                        item.name = prop.name
                                        item.propType = str(type(prop))
        else:
            self.outputs.clear()
            for socket in self.inputs:
                if not socket.bl_idname == "SN_SceneDataSocket":
                    self.inputs.remove(socket)
            self.search_properties.clear()


    def get_prop_identifier(self,name):
        for prop in eval("bpy.types."+self.current_data_type+".bl_rna.properties"):
            if prop.name == name:
                return prop.identifier
        return None


    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["INPUT"]

        inp = self.inputs.new('SN_SceneDataSocket', "Scene Data")
        inp.display_shape = "SQUARE"

        self.generate_sockets()

    def update(self):
        self.search_value = ""
        self.generate_sockets()

    def copy(self, node):
        self.search_value = ""
        self.previous_connection = ""
        self.current_data_type = ""
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

    def evaluate(self, output):
        code = []
        errors = []

        if self.has_collection_input:
            if self.inputs[0].is_linked:
                if self.inputs[0].links[0].from_socket.bl_idname == "SN_SceneDataSocket":
                    if output.name == "Amount":
                        code += ["len(", self.inputs[0].links[0].from_socket, ")"]
                    elif output.name == "Element":
                        if self.use_index:
                            value, error = get_input_value(self,"Index",["SN_IntSocket","SN_NumberSocket"])
                            code += [self.inputs[0].links[0].from_socket,"[",value,"]"]
                        else:
                            value, error = get_input_value(self,"Name",["SN_TextSocket"])
                            code += [self.inputs[0].links[0].from_socket,"['",value,"']"]
                        errors += error
                else:
                    errors.append("wrong_socket")

        else:
            if self.inputs[0].is_linked:
                if self.inputs[0].links[0].from_socket.bl_idname == "SN_SceneDataSocket":
                    identifier = self.get_prop_identifier(output.name)
                    if identifier:
                        code.append(self.inputs[0].links[0].from_socket)
                        code.append(".")
                        code.append(identifier)
                else:
                    errors.append("wrong_socket")

        return {"code": code, "error":errors}


    def all_string(self,code):
        for part in code:
            if type(part) != str:
                return False
        return True
        
        
    def internal_evaluate(self, output):
        code = self.evaluate(output)["code"]
        while not self.all_string(code):
            for i, part in enumerate(code):
                if not type(part) == str:
                    part = part.node.internal_evaluate(part)["code"]
                    code.pop(i)
                    code = code[:i] + part + code[i:]
                    break
        return {"code": code}
