#SN_GetPathNode

import os
import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_GetPathNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_GetPathNode"
    bl_label = "Get Path"
    bl_icon = "PARTICLE_DATA"
    node_color = (0.53, 0.55, 0.53)
    should_be_registered = False
    bl_width_default = 210

    docs = {
        "text": ["This node is used to <important>get different directory or file paths</>.",
                "You can use it to get the filepath to a blend file you want to append from or similar",
                ""],
        "python": ["os.path.dirname(os.path.realpath(__file__))"]

    }

    def inititialize(self, context):
        self.sockets.create_output(self, "STRING", "Python File")
        self.sockets.create_output(self, "STRING", "Blender File")

    def evaluate(self, socket, node_data, errors):
        if socket == self.outputs[1]:
            return {"blocks": [{"lines": [["os.path.dirname(bpy.data.filepath)"]],"indented": []}],"errors": errors}
        else:
            return {"blocks": [{"lines": [["get_python_filepath()"]],"indented": []}],"errors": errors}

    def required_imports(self):
        return ["bpy", "os"]
