#SN_AppendFromFileNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_AppendFromFileNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_AppendFromFileNode"
    bl_label = "Append from file"
    bl_icon = "CONSOLE"
    node_color = (0.2, 0.2, 0.2)
    bl_width_default = 300
    should_be_registered = False

    def update_file_path(self, context):
        if not self.file_path == bpy.path.abspath(self.file_path):
            self.file_path = bpy.path.abspath(self.file_path)

    def update_path(self, context):
        for inp in self.inputs:
            if inp.name == "Path":
                self.inputs.remove(inp)

        if not self.fixed_path:
            self.sockets.create_input(self,"STRING","Path")


    def getItems(self, context):
        items = ["Brush", "Camera", "Collection", "FreestyleLineStyle", "Image", "Image", "Light", "Material", "Mesh", "NodeTree", "Object", "Palette", "Scene", "Text", "Texture", "WorkSpace", "World"]

        tupleItems = []
        for item in items:
            tupleItems.append((item, item, ""))
        return tupleItems


    fixed_path: bpy.props.BoolProperty(name="Fixed Filepath", description="Fix the filepath", default=True, update=update_path)
    append_type: bpy.props.EnumProperty(items=getItems, name="Type", description="Type of the Append object")
    file_path: bpy.props.StringProperty(name="File Path", description="The path of the file", update=update_file_path, subtype="FILE_PATH")

    def inititialize(self,context):
        self.sockets.create_input(self,"EXECUTE","Execute")
        self.sockets.create_input(self,"STRING","Name")
        self.sockets.create_input(self,"BOOLEAN","Linked")
        self.sockets.create_output(self,"EXECUTE","Execute")

    def draw_buttons(self, context, layout):
        layout.prop(self, "append_type")
        layout.prop(self,"fixed_path")
        if self.fixed_path:
            layout.prop(self, "file_path")

    def evaluate(self, socket, node_data, errors):
        next_code = ""
        if node_data["output_data"][0]["code"]:
            next_code = node_data["output_data"][0]["code"]
        
        if self.fixed_path:
            filepath="r'" + self.file_path + "\\" + self.append_type + "'"
        else:
            filepath="r" + node_data["input_data"][3]["code"] + " + '\\" + self.append_type + "'"

        return {
            "blocks": [
                {
                    "lines": [
                        ["bpy.ops.wm.append(directory=", filepath, ", filename=", node_data["input_data"][1]["code"], ", link=", node_data["input_data"][2]["code"], ")"]
                    ],
                    "indented": [
                    ]
                },
                {
                    "lines": [
                        [next_code]
                    ],
                    "indented": [
                    ]
                }
            ],
            "errors": errors
        }
