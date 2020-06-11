import bpy
import os
from ..function_nodes.use_operator import SN_UseOperatorNode
from ..node_looks import node_colors, node_icons
from ...node_sockets import update_socket_autocompile
from ..node_utility import get_input_value


class SN_EnumItemPropertyGroup(bpy.types.PropertyGroup):

    identifier: bpy.props.StringProperty(name="Identifier", default="")
    name: bpy.props.StringProperty(name="Name", default="")
    description: bpy.props.StringProperty(name="Description", default="")
    socket: bpy.props.StringProperty(name="Description", default="")

class SN_AppendNode(bpy.types.Node):
    '''Node for using the append operator'''
    bl_idname = 'SN_AppendNode'
    bl_label = "Append"
    bl_icon = node_icons["OPERATOR"]
    bl_width_default = 300

    def update_file_path(self, context):
        if not self.file_path == bpy.path.abspath(self.file_path):
            self.file_path = bpy.path.abspath(self.file_path)


    def update_path(self, context):
        update_socket_autocompile(self, context)
        for inp in self.inputs:
            if inp.name == "Path":
                self.inputs.remove(inp)

        if self.fixed_path:
            pass
        else:
            self.inputs.new("SN_StringSocket", "Path")

    def getItems(self, context):
        items = ["Brush", "Camera", "Collection", "FreestyleLineStyle", "Image", "Image", "Light", "Material", "Mesh", "NodeTree", "Object", "Palette", "Scene", "Text", "Texture", "WorkSpace", "World"]

        tupleItems = []
        for item in items:
            tupleItems.append((item, item, ""))
        return tupleItems

    fixed_path: bpy.props.BoolProperty(name="Fixed Filepath", description="Fix the filepath", default=True, update=update_path)
    linked: bpy.props.BoolProperty(name="Link", description="Link", default=False, update=update_socket_autocompile)
    append_type: bpy.props.EnumProperty(items=getItems, name="Type", description="Type of the Append object", update=update_socket_autocompile)
    file_path: bpy.props.StringProperty(name="File Path", description="The path of the file", update=update_file_path, subtype="FILE_PATH")

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["OPERATOR"]

        inp = self.inputs.new('SN_ProgramSocket', "Program")
        inp.display_shape = "DIAMOND"

        self.inputs.new('SN_StringSocket', "Name")

        out = self.outputs.new('SN_ProgramSocket', "Program")
        out.display_shape = "DIAMOND"

    def draw_buttons(self, context, layout):
        layout.prop(self, "append_type")
        layout.prop(self,"linked")
        layout.prop(self,"fixed_path")
        if self.fixed_path:
            layout.prop(self, "file_path")

    def evaluate(self,output):
        code = []
        errors = []

        filepath = ["r"]
        if self.fixed_path:
            filepath.append("'" + self.file_path + "\\" + self.append_type + "'")
        else:
            path, error = get_input_value(self, "Path", "SN_StringSocket")
            errors+=error
            filepath+= path[:-1] + "\\" + self.append_type + "'"
        
        filename = ["filename="]
        if self.inputs["Name"].is_linked:
            filename.append(self.inputs["Name"].links[0].from_socket)
        else:
            filename.append("'" + self.inputs["Name"].value + "'")

        link = ["link="+str(self.linked)]

        return {"code": ["bpy.ops.wm.append(directory="] + filepath + [", "] + filename + [", "] + link + [")\n"], "error": errors}

