#SN_BranchNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_BranchNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_BranchNode"
    bl_label = "Branch (Layout)"
    bl_icon = "PARTICLE_DATA"
    node_color = (0.89,0.6,0)
    should_be_registered = False

    docs = {
        "text": ["The branch node <important>allows you to use the same layout type for multiple sockets</>.",
                ""],
        "python": []
    }


    def inititialize(self,context):
        self.sockets.create_input(self,"LAYOUT","Layout")
        self.sockets.create_output(self,"LAYOUT","Layout", True)

    def evaluate(self, socket, node_data, errors):
        branch_layout = []
        for output_data in node_data["output_data"]:
            if output_data["code"] != None:
                branch_layout.append([output_data["code"]])
    
        return {
            "blocks": [
                {
                    "lines": branch_layout,
                    "indented": [
                    ]
                }
            ],
            "errors": errors
        }

    def layout_type(self):
        if self.inputs[0].is_linked:
            if self.inputs[0].links[0].from_socket.bl_idname == self.inputs[0].bl_idname:
                return self.inputs[0].links[0].from_socket.node.layout_type()
        return "layout"

