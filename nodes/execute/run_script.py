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

    docs = {
        "text": ["This node is used to <important>run a script</>.",
                "",
                "<important>Make sure your script doesn't have functions and works before selecting it here</>"],
        "python": []

    }

    def inititialize(self, context):
        self.sockets.create_input(self, "EXECUTE", "Execute")
        self.sockets.create_output(self, "EXECUTE", "Execute")

    def update_outputs(self, context):
        if len(self.inputs) == 2:
            self.inputs.remove(self.inputs[1])
        if self.operation == "LINE":
            socket = self.sockets.create_input(self, "STRING", "Line")
            socket.is_string = False

    search_value: bpy.props.StringProperty(name="Search value", description="")
    operation: bpy.props.EnumProperty(items=[("SCRIPT", "Script", "Run a script"), ("LINE", "Single Line", "Run a single line")], name="Operation", update=update_outputs)

    def draw_buttons(self,context,layout):
        layout.prop(self, "operation", expand=True)
        if self.operation == "SCRIPT":
            layout.prop_search(self, "search_value", bpy.data, "texts", icon="TEXT", text="")

    def evaluate(self, socket, node_data, errors):
        next_code = ""
        if node_data["output_data"][0]["code"]:
            next_code = node_data["output_data"][0]["code"]

        script = []
        if self.operation == "SCRIPT":
            if self.search_value.lstrip() in bpy.data.texts:
                text = bpy.data.texts[self.search_value.lstrip()]
                script_text = text.as_string().split("\n")
                for line in script_text:
                    script.append([line])
        else:
            script = [[node_data["input_data"][1]["code"]]]

        return {
            "blocks": [
                {
                    "lines": script,
                    "indented": []
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
