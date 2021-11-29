import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_GetDataNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_GetDataNode"
    bl_label = "Get Data"

    data_path: bpy.props.StringProperty()

    def disect_data_path(self, path):
        # split data path in segments
        segments = path.split(".")[1:]
        # remove indexing from property name
        segments[-1] = segments[-1].split("[")[0]
        return segments

    def is_valid_data_path(self, path):
        return path and "bpy." in path and not ".ops." in path

    def get_data(self):
        if self.is_valid_data_path(self.data_path):
            return self.disect_data_path(self.data_path)
        return None

    def draw_node(self, context, layout):
        layout.prop(self, "data_path")
        layout.label(text=str(self.get_data()))

    def on_create(self, context):
        self.add_execute_input("Execute")
        self.add_execute_output("Execute")