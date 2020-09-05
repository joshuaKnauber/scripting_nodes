#SN_SetVariableNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_SetVariableNode(bpy.types.Node, SN_ScriptingBaseNode):
    bl_idname = "SN_SetVariableNode"
    bl_label = "Set Variable"
    bl_icon = "DRIVER_TRANSFORM"
    node_color = (0.75,0.75,0.75)
    should_be_registered = False
    bl_width_default = 225

    def inititialize(self, context):
        self.sockets.create_input(self, "EXECUTE", "Execute")
        self.sockets.create_output(self, "EXECUTE", "Execute")

    def update_outputs(self, context):
        if not self.search_value in bpy.context.space_data.node_tree.search_variables:
            for inp in range(len(self.inputs)-1):
                self.inputs.remove(self.inputs[1])

            if self.search_value != "":
                self.search_value = ""

        else:
            if bpy.context.space_data.node_tree.search_variables[self.search_value].is_array:
                self.update_operation(None)
                if len(self.inputs) == 2:
                    if self.inputs[1].name == bpy.context.space_data.node_tree.search_variables[self.search_value].name:
                        self.inputs.remove(self.inputs[1])
            else:
                if len(self.inputs) > 2:
                    for inp in self.inputs:
                        if inp.name != "Execute":
                            try:
                                self.inputs.remove(inp)
                            except RuntimeError:
                                pass
                
                if len(self.inputs) != 2:
                    self.sockets.create_input(self, bpy.context.space_data.node_tree.search_variables[self.search_value].socket_type, bpy.context.space_data.node_tree.search_variables[self.search_value].name)

                if bpy.context.space_data.node_tree.search_variables[self.search_value].name != self.inputs[1].name:
                    self.sockets.change_socket_type(self, self.inputs[1], bpy.context.space_data.node_tree.search_variables[self.search_value].socket_type, label=bpy.context.space_data.node_tree.search_variables[self.search_value].name)

                if self.inputs[1].bl_idname == "SN_VectorSocket":
                    self.inputs[1].use_four_numbers = bpy.context.space_data.node_tree.search_variables[self.search_value].type == "four_vector"

    def update_operation(self, context):
        if self.search_value in bpy.context.space_data.node_tree.search_variables:
            if bpy.context.space_data.node_tree.search_variables[self.search_value].is_array:
                identifiers = {"STRING": "SN_StringSocket", "BOOLEAN": "SN_BoolSocket", "INTEGER": "SN_IntSocket", "FLOAT": "SN_FloatSocket", "VECTOR": "SN_VectorSocket"}
                if self.operation == "set_value":
                    for inp in self.inputs:
                        if inp.name != "Index" and inp.name != "Execute" and inp.name != "Value":
                            try:
                                self.inputs.remove(inp)
                            except RuntimeError:
                                pass

                    if len(self.inputs) != 3:
                        self.sockets.create_input(self, "INTEGER", "Index")
                        self.sockets.create_input(self, bpy.context.space_data.node_tree.search_variables[self.search_value].socket_type, "Value")
                    
                    if self.inputs[2].bl_idname != identifiers[bpy.context.space_data.node_tree.search_variables[self.search_value].socket_type]:
                        self.sockets.change_socket_type(self, self.inputs[2], bpy.context.space_data.node_tree.search_variables[self.search_value].socket_type, label="Value")

                    if self.inputs[2].bl_idname == "SN_VectorSocket":
                        self.inputs[2].use_four_numbers = bpy.context.space_data.node_tree.search_variables[self.search_value].type == "four_vector"

                else:
                    for inp in self.inputs:
                        if inp.name != "Item Value" and inp.name != "Execute":
                            try:
                                self.inputs.remove(inp)
                            except RuntimeError:
                                pass
                    if len(self.inputs) < 2:
                        self.sockets.create_input(self, bpy.context.space_data.node_tree.search_variables[self.search_value].socket_type, "Item Value", dynamic=True)
                    if self.inputs[1].bl_idname != identifiers[bpy.context.space_data.node_tree.search_variables[self.search_value].socket_type]:
                        self.inputs.remove(self.inputs[1])
                        self.sockets.create_input(self, bpy.context.space_data.node_tree.search_variables[self.search_value].socket_type, "Item Value", dynamic=True)
                    
                    if self.inputs[1].bl_idname == "SN_VectorSocket":
                        for inp_index in range(len(self.inputs)-1):
                            self.inputs[inp_index+1].use_four_numbers = bpy.context.space_data.node_tree.search_variables[self.search_value].type == "four_vector"

    search_value: bpy.props.StringProperty(name="Search Value", description="", update=update_outputs)
    operation: bpy.props.EnumProperty(items=[("clear", "Clear and Replace", "Clear the Array and set new values"), ("set_value", "Set Value", "Set a value using an index")], name="Operation", description="", update=update_operation)

    def draw_buttons(self, context, layout):
        col = layout.column()
        col.scale_y = 1.25
        col.prop_search(self,"search_value", bpy.context.space_data.node_tree, "search_variables", text="")

        if self.search_value in bpy.context.space_data.node_tree.search_variables:
            if bpy.context.space_data.node_tree.search_variables[self.search_value].description != "":
                box = col.box()
                box.label(text=bpy.context.space_data.node_tree.search_variables[self.search_value].description)
            if bpy.context.space_data.node_tree.search_variables[self.search_value].is_array:
                if len(self.inputs) == 2:
                    if self.inputs[1].name == bpy.context.space_data.node_tree.search_variables[self.search_value].name:
                        self.inputs.remove(self.inputs[1])
                row = col.row()
                row.prop(self, "operation", expand=True)
            else:
                if len(self.inputs) != 2:
                    self.sockets.create_input(self, bpy.context.space_data.node_tree.search_variables[self.search_value].socket_type, bpy.context.space_data.node_tree.search_variables[self.search_value].name)

    def update(self):
        self.update_dynamic(True)
        self.update_dynamic(False)
        for input_socket in self.inputs:
            for link in input_socket.links:
                link.from_node.update()
                
        self.update_socket_connections()
        self.update_operation(None)

    def evaluate(self, socket, node_data, errors):
        next_code = ""
        if node_data["output_data"][0]["code"]:
            next_code = node_data["output_data"][0]["code"]

        blocks = [{"lines": [],"indented": []}]
        if self.search_value in bpy.context.space_data.node_tree.search_variables:
            if bpy.context.space_data.node_tree.search_variables[self.search_value].is_array:
                if self.operation == "set_value":
                    blocks = [{"lines": [["bpy.context.scene.sn_generated_addon_properties_UID_." + bpy.context.space_data.node_tree.search_variables[self.search_value].name + "_array[", node_data["input_data"][1]["code"], "]." + bpy.context.space_data.node_tree.search_variables[self.search_value].type, " = ", node_data["input_data"][2]["code"]]],"indented": []}]

                else:
                    items = [["bpy.context.scene.sn_generated_addon_properties_UID_." + bpy.context.space_data.node_tree.search_variables[self.search_value].name + "_array.clear()"]]
                    for inp_index in range(len(self.inputs)-1):
                        items.append(["bpy.context.scene.sn_generated_addon_properties_UID_." + bpy.context.space_data.node_tree.search_variables[self.search_value].name + "_array.add().", bpy.context.space_data.node_tree.search_variables[self.search_value].type, " = ", node_data["input_data"][inp_index+1]["code"]])

                    blocks = [{"lines": items,"indented": []}]

            else:
                blocks = [{"lines": [["bpy.context.scene.sn_generated_addon_properties_UID_." + bpy.context.space_data.node_tree.search_variables[self.search_value].name, " = ", node_data["input_data"][1]["code"]]],"indented": []}]

        return {"blocks": blocks + [{"lines": [[next_code]],"indented": []}], "errors": errors}

