#SN_RunScriptNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode
from ...node_tree.node_sockets import is_valid_python, make_valid_python

class SN_RunScriptNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_RunScriptNode"
    bl_label = "Run Script"
    bl_icon = "FILE_SCRIPT"
    node_color = (0.2, 0.2, 0.2)
    should_be_registered = False

    def inititialize(self, context):
        self.sockets.create_input(self, "EXECUTE", "Execute")
        self.sockets.create_output(self, "EXECUTE", "Execute")

    search_value: bpy.props.StringProperty(name="Search value", description="")

    def draw_buttons(self,context,layout):
        layout.prop_search(self, "search_value", bpy.data, "texts", icon="TEXT", text="")

    def evaluate(self, socket, input_data, errors):
        script = ""
        if self.search_value.lstrip() in bpy.data.texts:
            text = bpy.data.texts[self.search_value.lstrip()]
            script = text.as_string()

        return {
            "blocks": [
                {
                    "lines": [
                        [script]
                    ],
                    "indented": [
                    ]
                }
            ],
            "errors": errors
        }
