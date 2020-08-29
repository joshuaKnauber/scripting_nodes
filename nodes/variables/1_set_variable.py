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

    def update_outputs(self, context):
        if self.search_value == "":
            if self.inputs[1].bl_idname != "SN_DataSocket":
                self.sockets.change_socket_type(self, self.inputs[1], "DATA", label=" ")
        elif not self.search_value in bpy.context.scene.sn_properties.search_variables:
            self.search_value = ""
            if self.inputs[1].bl_idname != "SN_DataSocket":
                self.sockets.change_socket_type(self, self.inputs[1], "DATA", label=" ")
        else:
            self.sockets.change_socket_type(self, self.inputs[1], bpy.context.scene.sn_properties.search_variables[self.search_value].socket_type, label=bpy.context.scene.sn_properties.search_variables[self.search_value].name)

    search_value: bpy.props.StringProperty(name="Search Value", description="", update=update_outputs)

    def draw_buttons(self, context, layout):
        row = layout.row()
        row.scale_y = 1.25
        row.prop_search(self,"search_value", bpy.context.scene.sn_properties, "search_variables", text="")

        if not self.search_value in bpy.context.scene.sn_properties.search_variables:
            if self.inputs[1].bl_idname != "SN_DataSocket":
                self.sockets.change_socket_type(self, self.inputs[1], "DATA", label=" ")

    def evaluate(self, socket, input_data, errors):
        if self.search_value in bpy.context.scene.sn_properties.search_variables:
            if bpy.context.scene.sn_properties.search_variables[self.search_value].is_array:
                blocks = [{"lines": [["bpy.context.scene.sn_generated_addon_properties_UID_." + bpy.context.scene.sn_properties.search_variables[self.search_value].name + "_array"]],"indented": []}]
            else:
                blocks = [{"lines": [["bpy.context.scene.sn_generated_addon_properties_UID_." + bpy.context.scene.sn_properties.search_variables[self.search_value].name]],"indented": []}]
        else:
            blocks = [{"lines": [["None"]],"indented": []}]
        return {"blocks": blocks, "errors": errors}

