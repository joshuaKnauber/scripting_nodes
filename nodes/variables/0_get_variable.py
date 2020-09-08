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

    def update_outputs(self, context):
        if self.search_value == "":
            if len(self.outputs) == 3:
                self.outputs.remove(self.outputs[1])
                self.outputs.remove(self.outputs[1])
            if len(self.inputs) == 1:
                self.inputs.remove(self.inputs[0])
            if self.outputs[0].bl_idname != "SN_DataSocket":
                self.sockets.change_socket_type(self, self.outputs[0], "DATA", label=" ")
        elif not self.search_value in bpy.context.space_data.node_tree.search_variables:
            if len(self.outputs) == 3:
                self.outputs.remove(self.outputs[1])
                self.outputs.remove(self.outputs[1])
            if len(self.inputs) == 1:
                self.inputs.remove(self.inputs[0])

            self.search_value = ""
            if self.outputs[0].bl_idname != "SN_DataSocket":
                self.sockets.change_socket_type(self, self.outputs[0], "DATA", label=" ")
        else:
            if bpy.context.space_data.node_tree.search_variables[self.search_value].is_array:
                if len(self.outputs) != 3:
                    self.sockets.create_output(self, "INTEGER", "Length")
                    self.sockets.create_output(self, "BOOLEAN", "Is empty")
                if len(self.inputs) != 1:
                    self.sockets.create_input(self, "INTEGER", "Index").set_value(0)
            else:
                if len(self.outputs) == 3:
                    self.outputs.remove(self.outputs[1])
                    self.outputs.remove(self.outputs[1])
                if len(self.inputs) == 1:
                    self.inputs.remove(self.inputs[0])
            self.sockets.change_socket_type(self, self.outputs[0], bpy.context.space_data.node_tree.search_variables[self.search_value].socket_type, label=bpy.context.space_data.node_tree.search_variables[self.search_value].name)
            if self.outputs[0].bl_idname == "SN_VectorSocket":
                self.outputs[0].use_four_numbers = bpy.context.space_data.node_tree.search_variables[self.search_value].type == "four_vector" or bpy.context.space_data.node_tree.search_variables[self.search_value].type == "four_color"

    search_value: bpy.props.StringProperty(name="Search Value", description="", update=update_outputs)

    def draw_buttons(self, context, layout):
        col = layout.column()
        col.scale_y = 1.25
        col.prop_search(self,"search_value", bpy.context.space_data.node_tree, "search_variables", text="")

        if not self.search_value in bpy.context.space_data.node_tree.search_variables:
            if len(self.outputs) == 3:
                self.outputs.remove(self.outputs[1])
                self.outputs.remove(self.outputs[1])
            if len(self.inputs) == 1:
                self.inputs.remove(self.inputs[0])
            if self.outputs[0].bl_idname != "SN_DataSocket":
                self.sockets.change_socket_type(self, self.outputs[0], "DATA", label=" ")
        else:
            if bpy.context.space_data.node_tree.search_variables[self.search_value].description != "":
                box = col.box()
                box.label(text=bpy.context.space_data.node_tree.search_variables[self.search_value].description)

    def evaluate(self, socket, node_data, errors):
        blocks = [{"lines": [["None"]],"indented": []}]
        if self.search_value in bpy.context.space_data.node_tree.search_variables:
            if bpy.context.space_data.node_tree.search_variables[self.search_value].is_array:
                if socket == self.outputs[0]:
                    blocks = [{"lines": [["bpy.context.scene.sn_generated_addon_properties_UID_." + bpy.context.space_data.node_tree.search_variables[self.search_value].name + "_array[", node_data["input_data"][0]["code"], "]." + bpy.context.space_data.node_tree.search_variables[self.search_value].type]],"indented": []}]
                elif socket == self.outputs[1]:
                    blocks = [{"lines": [["len(bpy.context.scene.sn_generated_addon_properties_UID_." + bpy.context.space_data.node_tree.search_variables[self.search_value].name + "_array)"]],"indented": []}]
                elif socket == self.outputs[2]:
                    blocks = [{"lines": [["len(bpy.context.scene.sn_generated_addon_properties_UID_." + bpy.context.space_data.node_tree.search_variables[self.search_value].name + "_array) == 0"]],"indented": []}]
            else:
                blocks = [{"lines": [["bpy.context.scene.sn_generated_addon_properties_UID_." + bpy.context.space_data.node_tree.search_variables[self.search_value].name]],"indented": []}]
        return {"blocks": blocks, "errors": errors}

