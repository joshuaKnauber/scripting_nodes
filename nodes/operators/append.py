import bpy
from ..base.base_node import SN_ScriptingBaseNode
from ...compile.compiler import compiler
from ..base.node_looks import node_colors, node_icons


class SN_AppendNode(bpy.types.Node, SN_ScriptingBaseNode):
    
    bl_idname = "SN_AppendNode"
    bl_label = "Append from file"
    bl_icon = node_icons["OPERATOR"]
    bl_width_default = 300

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'ScriptingNodesTree'

    def socket_update(self, context):
        compiler().socket_update()

    def update_file_path(self, context):
        if not self.file_path == bpy.path.abspath(self.file_path):
            self.file_path = bpy.path.abspath(self.file_path)

        self.socket_update(context)


    def update_path(self, context):
        for inp in self.inputs:
            if inp.name == "Path":
                self.inputs.remove(inp)

        if self.fixed_path:
            pass
        else:
            self.inputs.new("SN_StringSocket", "Path")
        
        self.socket_update(context)

    def getItems(self, context):
        items = ["Brush", "Camera", "Collection", "FreestyleLineStyle", "Image", "Image", "Light", "Material", "Mesh", "NodeTree", "Object", "Palette", "Scene", "Text", "Texture", "WorkSpace", "World"]

        tupleItems = []
        for item in items:
            tupleItems.append((item, item, ""))
        return tupleItems

    fixed_path: bpy.props.BoolProperty(name="Fixed Filepath", description="Fix the filepath", default=True, update=update_path)
    append_type: bpy.props.EnumProperty(items=getItems, name="Type", description="Type of the Append object", update=socket_update)
    file_path: bpy.props.StringProperty(name="File Path", description="The path of the file", update=update_file_path, subtype="FILE_PATH")

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["OPERATOR"]

        self.inputs.new('SN_ProgramSocket', "Program").display_shape = "DIAMOND"
        self.inputs.new('SN_StringSocket', "Name")
        self.inputs.new('SN_BooleanSocket', "Linked")

        self.outputs.new('SN_ProgramSocket', "Program").display_shape = "DIAMOND"

    def draw_buttons(self, context, layout):
        layout.prop(self, "append_type")
        layout.prop(self,"fixed_path")
        if self.fixed_path:
            layout.prop(self, "file_path")

    def evaluate(self,output):
        errors = []

        if self.fixed_path:
            filepath=["r\"" + self.file_path + "\\" + self.append_type + "\""]
        else:
            path, error = self.SocketHandler.socket_value(self.inputs["Path"])
            errors+=error
            if path != "":
                filepath=["r"] + path + [" + \"\\" + self.append_type + "\""]
            else:
                filepath=["r" + self.append_type + "\""]

        filename, error = self.SocketHandler.socket_value(self.inputs[1])
        filename = ["filename="] + filename
        errors+=error

        link, error = self.SocketHandler.socket_value(self.inputs[2])
        link = ["link="] + link
        errors+=error
        continue_code, error = self.SocketHandler.socket_value(self.outputs[0])
        errors+=error

        return {
            "blocks": [
                {
                    "lines": [
                        ["bpy.ops.wm.append(directory="] + filepath + [", "] + filename + [", "] + link + [")\n"]
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
        return ["bpy"]