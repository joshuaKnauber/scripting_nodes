import bpy
from ..base.base_node import SN_ScriptingBaseNode
from ...compile.compiler import compiler
from ..base.node_looks import node_colors, node_icons


class SN_ChangeVariable(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_ChangeVariable"
    bl_label = "Change Variable"
    bl_icon = node_icons["PROGRAM"]

    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'ScriptingNodesTree'

    def socket_update(self, context):
        compiler().socket_update()

    def connected_nodes(self, node):
        nodes = []
        for inp in node.inputs:
            if inp.is_linked:
                nodes.append(inp.links[0].from_node)
        return nodes

    def items_fetch(self, context):
        all_nodes = []
        if self.inputs[0].is_linked:
            all_nodes = [self.inputs[0].links[0].to_node]

        found_new_node = True
        while found_new_node:
            found_new_node = False
            for node in all_nodes:
                for connected in self.connected_nodes(node):
                    if not connected in all_nodes:
                        all_nodes.append(connected)
                        found_new_node = True

        variable_nodes = []
        for node in all_nodes:
            if node.bl_idname == "SN_CreateVariable":
                if node.variable_name != "":
                    variable_identifier = self.ErrorHandler.handle_text(str(node.variable_name))
                    variable_nodes.append((variable_identifier, str(node.variable_name), ""))

        return variable_nodes

    variable: bpy.props.EnumProperty(items=items_fetch, name="Variable", description="The name of the variable", update=socket_update)

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["PROGRAM"]

        self.inputs.new("SN_ProgramSocket", "Program").display_shape = "DIAMOND"
        self.inputs.new("SN_DataSocket", "Output")
        self.outputs.new("SN_ProgramSocket", "Program").display_shape = "DIAMOND"

    def draw_buttons(self, context, layout):
        layout.prop(self,"variable")

    def evaluate(self, output):
        errors = []
        variable = self.variable
        if variable == "":
            variable = "test"
            errors.append({"error": "no_var_available", "node": self})

        value, error = self.SocketHandler.socket_value(self.inputs[1])
        errors+=error
        continue_code, error = self.SocketHandler.socket_value(self.outputs[0], False)
        errors+=error
        return {
            "blocks": [
                {
                    "lines": [
                        [variable + " = "] + value
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
        return []