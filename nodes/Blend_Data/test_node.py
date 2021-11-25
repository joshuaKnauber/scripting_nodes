import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode



class SN_GetDataNodeee(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_GetDataNodeee"
    bl_label = "Get Data (new)"
    # bl_icon = "GRAPH"
    bl_width_default = 160
    
    node_options = {
        "default_color": (0.3,0.3,0.3),
    }

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

    def draw_node(self,context,layout):
        layout.prop(self, "data_path")
        layout.label(text=str(self.get_data()))