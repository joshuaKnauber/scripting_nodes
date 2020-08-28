#SN_SetVariableNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_SetVariableNode(bpy.types.Node, SN_ScriptingBaseNode):
    bl_idname = "SN_SetVariableNode"
    bl_label = "Set Variable"
    bl_icon = "DRIVER_TRANSFORM"
    node_color = (0.75,0.75,0.75)
    should_be_registered = False

    def inititialize(self, context):
        self.sockets.create_input(self, "EXECUTE", "Execute")
        self.sockets.create_input(self, "DATA", "")
        self.sockets.create_output(self, "EXECUTE", "Execute")

    def get_variables(self, context):
        items = [("None", "No selection", "Please select or create a variable")]
        identifiers = [
            "SN_BooleanVariableNode",
            "SN_FloatVariableNode",
            "SN_IntegerVariableNode",
            "SN_StringVariableNode",
            "SN_VectorVariableNode",
        ]
        if hasattr(bpy.context.space_data, "node_tree"):
            for node in bpy.context.space_data.node_tree.nodes:
                if node.bl_idname in identifiers:
                    if not node.is_array:
                        items.append((node.var_name.replace(" ", "_"),node.var_name,node.description))
                    else:
                        items.append((node.var_name.replace(" ", "_") + "_array",node.var_name,node.description))

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

        if self.variables != "None":
            for node in bpy.context.space_data.node_tree.nodes:
                if node.bl_idname in ["SN_BooleanVariableNode", "SN_FloatVariableNode", "SN_IntegerVariableNode", "SN_StringVariableNode", "SN_VectorVariableNode"]:
                    if node.var_name == self.variables:
                        if socket_identifiers[node.bl_idname][0] != self.inputs[1].bl_idname or node.var_name != self.inputs[1].name:
                            self.sockets.change_socket_type(self, self.inputs[1], socket_identifiers[node.bl_idname][1], label=node.var_name)

        else:
            if self.inputs[1].bl_idname != "SN_DataSocket":
                self.sockets.change_socket_type(self, self.inputs[1], "DATA", label=" ")

        row = layout.row()
        row.scale_y = 1.25
        row.prop(self,"variables",text="")

    def evaluate(self, socket, input_data, errors):
        if self.variables != "None":
            blocks = [{"lines": [["bpy.context.scene.sn_generated_addon_properties_UID_." + self.variables]],"indented": []}]
        else:
            blocks = [{"lines": [["None"]],"indented": []}]
        return {"blocks": blocks, "errors": errors}

