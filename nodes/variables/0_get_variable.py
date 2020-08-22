#SN_GetVariableNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_GetVariableNode(bpy.types.Node, SN_ScriptingBaseNode):
    bl_idname = "SN_GetVariableNode"
    bl_label = "Get Variable"
    bl_icon = "DRIVER_TRANSFORM"
    node_color = (0.75,0.75,0.75)
    should_be_registered = False

    def inititialize(self, context):
        self.sockets.create_output(self, "DATA", "")

    def get_variables(self,context):
        items = []
        identifiers = [
            "SN_BooleanVariableNode",
            "SN_FloatVariableNode",
            "SN_IntegerVariableNode",
            "SN_StringVariableNode",
            "SN_VectorVariableNode",
        ]
        for node in context.space_data.node_tree.nodes:
            if node.bl_idname in identifiers:
                items.append((node.var_name,node.var_name,node.description))

        return items

    variables: bpy.props.EnumProperty(items=get_variables,name="Variable",description="The variable you want to get the value from")

    def draw_buttons(self, context, layout):
        socket_identifiers = {
            "SN_BooleanVariableNode": ["SN_BoolSocket", "BOOLEAN"],
            "SN_FloatVariableNode": ["SN_FloatSocket", "FLOAT"],
            "SN_IntegerVariableNode": ["SN_IntSocket", "INTEGER"],
            "SN_StringVariableNode": ["SN_StringSocket", "STRING"],
            "SN_VectorVariableNode": ["SN_VectorSocket", "VECTOR"]
        }

        if self.variables != "":
            for node in bpy.context.space_data.node_tree.nodes:
                if node.bl_idname in ["SN_BooleanVariableNode", "SN_FloatVariableNode", "SN_IntegerVariableNode", "SN_StringVariableNode", "SN_VectorVariableNode"]:
                    if node.var_name == self.variables:
                        if socket_identifiers[node.bl_idname][0] != self.outputs[0].bl_idname or node.var_name != self.outputs[0].name:
                            self.sockets.change_socket_type(self, self.outputs[0], socket_identifiers[node.bl_idname][1], label=node.var_name)
        else:
            if self.outputs[0].bl_idname != "SN_DataSocket":
                self.sockets.change_socket_type(self, self.outputs[0], "DATA", label=" ")

        row = layout.row()
        row.scale_y = 1.25
        row.prop(self,"variables",text="")

    def evaluate(self, socket, input_data, errors):
        blocks = []
        return {"blocks": blocks, "errors": errors}
