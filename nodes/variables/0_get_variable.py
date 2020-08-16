#SN_GetVariableNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_GetVariableNode(bpy.types.Node, SN_ScriptingBaseNode):
    bl_idname = "SN_GetVariableNode"
    bl_label = "Get Variable"
    bl_icon = "DRIVER_TRANSFORM"
    node_color = (0.75,0.75,0.75)
    should_be_registered = False

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
                items.append((node.name,node.var_name,node.description))

        return items

    def update_socket_output(self, context):
        identifiers = {
            "SN_BooleanVariableNode": "BOOLEAN",
            "SN_FloatVariableNode": "FLOAT",
            "SN_IntegerVariableNode": "INTEGER",
            "SN_StringVariableNode": "STRING",
            "SN_VectorVariableNode": "VECTOR",
        }

        socket_identifiers = {
            "SN_BooleanVariableNode": "SN_BoolSocket",
            "SN_FloatVariableNode": "SN_FloatSocket",
            "SN_IntegerVariableNode": "SN_IntSocket",
            "SN_StringVariableNode": "SN_StringSocket",
            "SN_VectorVariableNode": "SN_VectorSocket",
        }

        if self.variables != "":
            if not len(self.outputs):     
                for node in context.space_data.node_tree.nodes:
                    if node.name == self.variables:
                        self.sockets.create_output(self, identifiers[node.bl_idname], node.var_name)
            else:
                for node in context.space_data.node_tree.nodes:
                    if node.name == self.variables:
                        if socket_identifiers[node.bl_idname] != self.outputs[0].bl_idname or node.var_name != self.outputs[0].name:
                            self.sockets.change_socket_type(self, self.outputs[0], identifiers[node.bl_idname], label=node.var_name)
        else:
            self.outputs.clear()

    variables: bpy.props.EnumProperty(items=get_variables,name="Variable",description="The variable you want to get the value from", update=update_socket_output)

    def draw_buttons(self, context, layout):
        row = layout.row()
        row.scale_y = 1.25
        row.prop(self,"variables",text="")

    def evaluate(self, socket, input_data, errors):
        blocks = []
        return {"blocks": blocks, "errors": errors}
