#SN_KeymapNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode
from ...node_tree.node_sockets import is_valid_python, make_valid_python
from uuid import uuid4

class SN_KeymapNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_KeymapNode"
    bl_label = "Keymap"
    bl_icon = "FILE_SCRIPT"
    node_color = (0.2, 0.2, 0.2)
    should_be_registered = True

    docs = {
        "text": ["This node is used to <important>run a script</>.",
                "",
                "<important>Make sure your script doesn't have functions and works before selecting it here</>"],
        "python": []

    }

    keymap_uid: bpy.props.StringProperty()

    def inititialize(self, context):
        self.keymap_uid = uuid4().hex[:10]

    def copy(self,context):
        self.keymap_uid = uuid4().hex[:10]

    def draw_buttons(self,context,layout):
        pass

    def function_name(self):
        return "register_keymap_"+self.keymap_uid

    def get_register_block(self):
        return [self.function_name()+"()"]

    def get_unregister_block(self):
        return []

    def evaluate(self, socket, node_data, errors):
        return {"blocks": [
            {
                "lines": [
                    ["def ",self.function_name(),"():"]
                ],
                "indented": [
                    ["global addon_keymaps"]
                ]
            }
        ],"errors": errors}
