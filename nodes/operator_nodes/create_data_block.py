import bpy
from ..base_node import SN_ScriptingBaseNode
from ..node_looks import node_colors, node_icons
from ..node_utility import register_dynamic_input, get_input_value, get_types, get_data_blocks
from ...node_sockets import update_socket_autocompile


class SN_CreateDataNode(bpy.types.Node, SN_ScriptingBaseNode):
    '''Node to create a data block'''
    bl_idname = 'SN_CreateDataNode'
    bl_label = "Create Data Block"
    bl_icon = node_icons["OPERATOR"]
    bl_width_default = 275

    def updateLoc(self, context):
        update_socket_autocompile(self, context)
        self.generate_sockets()

    def get_socket_items(self, context):
        data = get_data_blocks()[self.propLocation]
        for socket in data:
            if socket[0] == "SN_EnumSocket":
                return socket[2]

    def generate_sockets(self):
        if self.propLocation != "":
            for inp in self.inputs:
                if inp.bl_idname != "SN_ProgramSocket" and inp.bl_idname != "SN_StringSocket":
                    self.inputs.remove(inp)
            data = get_data_blocks()[self.propLocation]
            for socket in data:
                if socket[0] != "SN_EnumSocket" and socket[1] != "Name":
                    self.inputs.new(socket[0], socket[1])
                elif socket[1] != "Name":
                    self.inputs.new(socket[0], socket[1])

    def getItems(self, context):
        items = []

        for obj in dir(bpy.data):
            if "new" in eval("dir(bpy.data."+obj+")"):
                if obj != "objects":
                    items.append((obj, obj.replace("_", " ").title(), ""))

        return items

    propLocation: bpy.props.EnumProperty(items=getItems, name="Location", description="Location of the data", update=updateLoc)
    var_name: bpy.props.StringProperty(default="data_var_0")

    def get_var_name(self):
        highest_var_name = 0
        for node in bpy.context.space_data.node_tree.nodes:
            if node.bl_idname == self.bl_idname:
                number = int(node.var_name.split("_")[-1])
                highest_var_name = max(number,highest_var_name)
        return "data_var_"+str(highest_var_name + 1)

    def init(self, context):
        self.var_name = self.get_var_name()
        pIn = self.inputs.new('SN_ProgramSocket', "Program")
        pIn.display_shape = "DIAMOND"
        self.inputs.new('SN_StringSocket', "Name")

        self.generate_sockets()
        self.use_custom_color = True
        self.color = node_colors["OPERATOR"]

        pOut = self.outputs.new('SN_ProgramSocket', "Program")
        pOut.display_shape = "DIAMOND"

        self.outputs.new('SN_DataSocket', "Output")

    def copy(self, node):
        self.var_name = self.get_var_name()

    def free(self):
        pass# called when node is removed

    def draw_buttons(self, context, layout):
        layout.prop(self,"propLocation")

    def evaluate(self,output):
        if output == self.outputs[-1]:
            return {"code":[self.var_name]}
        
        errors = []
        code = []

        if self.inputs[1].is_linked:
            name, error = get_input_value(self, "Name", "SN_StringSocket")
            errors+=(error)
        else:
            name = "'" + self.inputs[1].value + "'"

        code.append(self.var_name)
        code.append(" = bpy.data.")
        code.append(self.propLocation)
        code.append(".new(")
        if name != "''":
            code.append(name)
            if len(self.inputs) == 2:
                code.append(")\n")
            elif len(self.inputs) == 3:
                code.append(", ")
                if self.inputs[2].is_linked:
                    name, error = get_input_value(self, 2, ["SN_StringSocket"])
                    errors+=(error)
                else:
                    name = "'" + str(self.inputs[2].value) + "', "
                code.append(name)
                code.append(")\n")

            elif self.propLocation == "images":
                code.append(", ")

                if self.inputs["Width"].is_linked:
                    name, error = get_input_value(self, "Width", "SN_IntSocket")
                    errors+=(error)
                else:
                    name = str(self.inputs["Width"].value) + ", "
                code.append(name)

                if self.inputs["Height"].is_linked:
                    name, error = get_input_value(self, "Height", "SN_IntSocket")
                    errors+=(error)
                else:
                    name = str(self.inputs["Height"].value) + ", "
                code.append(name)

                if self.inputs["Alpha"].is_linked:
                    name, error = get_input_value(self, "Alpha", "SN_BooleanSocket")
                    errors+=(error)
                else:
                    name = str(self.inputs["Alpha"].value) + ", "
                code.append(name)

                if self.inputs["Float Buffer"].is_linked:
                    name, error = get_input_value(self, "Float Buffer", "SN_BooleanSocket")
                    errors+=(error)
                else:
                    name = str(self.inputs["Float Buffer"].value) + ", "
                code.append(name)

                if self.inputs["Stereo 3D"].is_linked:
                    name, error = get_input_value(self, "Stereo 3D", "SN_BooleanSocket")
                    errors+=(error)
                else:
                    name = str(self.inputs["Stereo 3D"].value) + ", "
                code.append(name)

                if self.inputs["Is True"].is_linked:
                    name, error = get_input_value(self, "Is True", "SN_BooleanSocket")
                    errors+=(error)
                else:
                    name = str(self.inputs["Is True"].value) + ", "
                code.append(name)

                if self.inputs["Tiled"].is_linked:
                    name, error = get_input_value(self, "Tiled", "SN_BooleanSocket")
                    errors+=(error)
                else:
                    name = str(self.inputs["Tiled"].value)
                code.append(name)

                code.append(")\n")
        else:
            code=[]
            errors.append("no_name_data")

        
        return {"code": code, "error":errors}
