#SN_AddToArrayVariableNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_AddToArrayVariableNode(bpy.types.Node, SN_ScriptingBaseNode):
    bl_idname = "SN_AddToArrayVariableNode"
    bl_label = "Add to Array"
    bl_icon = "DRIVER_TRANSFORM"
    node_color = (0.75,0.75,0.75)
    should_be_registered = False

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
                    if self.inputs[1].bl_idname == "SN_VectorSocket":
                        self.inputs[1].use_four_numbers = bpy.context.space_data.node_tree.search_variables[self.search_value].type == "four_vector"
                if len(self.inputs) == 3:
                    if self.inputs[2].bl_idname == "SN_VectorSocket":
                        self.inputs[2].use_four_numbers = bpy.context.space_data.node_tree.search_variables[self.search_value].type == "four_vector"

            else:
                for inp in range(len(self.inputs)-1):
                    self.inputs.remove(self.inputs[1])

    def update_operation(self, context):
        if self.search_value in bpy.context.space_data.node_tree.search_variables:
            if bpy.context.space_data.node_tree.search_variables[self.search_value].is_array:
                identifiers = {"STRING": "SN_StringSocket", "BOOLEAN": "SN_BoolSocket", "INTEGER": "SN_IntSocket", "FLOAT": "SN_FloatSocket", "VECTOR": "SN_VectorSocket"}
                if self.operation == "index":
                    if len(self.inputs) != 3:
                        for inp in range(len(self.inputs)-1):
                            self.inputs.remove(self.inputs[1])

                    if len(self.inputs) != 3:
                        self.sockets.create_input(self, "INTEGER", "Index").set_value(0)
                        self.sockets.create_input(self, bpy.context.space_data.node_tree.search_variables[self.search_value].socket_type, bpy.context.space_data.node_tree.search_variables[self.search_value].name)
                    if self.inputs[2].bl_idname == "SN_VectorSocket":
                        self.inputs[2].is_color = bpy.context.space_data.node_tree.search_variables[self.search_value].type == "color" or bpy.context.space_data.node_tree.search_variables[self.search_value].type == "four_color"
                        self.inputs[2].use_four_numbers = bpy.context.space_data.node_tree.search_variables[self.search_value].type == "four_vector" or bpy.context.space_data.node_tree.search_variables[self.search_value].type == "four_color"

                else:
                    if len(self.inputs) != 2:
                        for inp in range(len(self.inputs)-1):
                            self.inputs.remove(self.inputs[1])

                    if len(self.inputs) != 2:
                        self.sockets.create_input(self, bpy.context.space_data.node_tree.search_variables[self.search_value].socket_type, bpy.context.space_data.node_tree.search_variables[self.search_value].name)
                    
                    if self.inputs[1].bl_idname == "SN_VectorSocket":
                        self.inputs[1].is_color = bpy.context.space_data.node_tree.search_variables[self.search_value].type == "color" or bpy.context.space_data.node_tree.search_variables[self.search_value].type == "four_color"
                        self.inputs[1].use_four_numbers = bpy.context.space_data.node_tree.search_variables[self.search_value].type == "four_vector" or bpy.context.space_data.node_tree.search_variables[self.search_value].type == "four_color"


    search_value: bpy.props.StringProperty(name="Search Value", description="", update=update_outputs)
    operation: bpy.props.EnumProperty(items=[("start", "Start", "The first element in the array"), ("end", "End", "The last element in the array"), ("index", "Index", "Set a value using an index")], name="Operation", description="", update=update_operation)

    def draw_buttons(self, context, layout):
        col = layout.column()
        col.scale_y = 1.25
        col.prop_search(self,"search_value", bpy.context.space_data.node_tree, "search_variables", text="")

        if self.search_value in bpy.context.space_data.node_tree.search_variables:
            if bpy.context.space_data.node_tree.search_variables[self.search_value].is_array:
                self.update_operation("None")
                if bpy.context.space_data.node_tree.search_variables[self.search_value].description != "":
                    box = col.box()
                    box.label(text=bpy.context.space_data.node_tree.search_variables[self.search_value].description)

                row = col.row()
                row.prop(self, "operation", expand=True)

            else:
                for inp in range(len(self.inputs)-1):
                    self.inputs.remove(self.inputs[1])
                box = col.box()
                box.label(text="Please select an array")
        else:
            for inp in range(len(self.inputs)-1):
                self.inputs.remove(self.inputs[1])
            box = col.box()
            box.label(text="Please select an array")

    def get_vector(self, socket):
        value = ""
        if socket.use_four_numbers:
            if not socket.is_linked:
                value = (socket.get_value()[0], socket.get_value()[1], socket.get_value()[2], socket.get_value()[3])

        else:
            if not socket.is_linked:
                value = (socket.get_value()[0], socket.get_value()[1], socket.get_value()[2])
        value = str(value)
        if socket.is_linked:
            value = socket.links[0].from_socket

        return value

    def evaluate(self, socket, node_data, errors):
        next_code = ""
        if node_data["output_data"][0]["code"]:
            next_code = node_data["output_data"][0]["code"]

        blocks = [{"lines": [],"indented": []}]
        if self.search_value in bpy.context.space_data.node_tree.search_variables:
            if bpy.context.space_data.node_tree.search_variables[self.search_value].is_array:
                if self.operation == "index":
                    add_text = ["bpy.context.scene.sn_generated_addon_properties_UID_." + bpy.context.space_data.node_tree.search_variables[self.search_value].name + "_array.add().", bpy.context.space_data.node_tree.search_variables[self.search_value].type, " = ", node_data["input_data"][2]["code"]]
                    blocks = [{"lines": [add_text, ["bpy.context.scene.sn_generated_addon_properties_UID_." + bpy.context.space_data.node_tree.search_variables[self.search_value].name + "_array.move(len(bpy.context.scene.sn_generated_addon_properties_UID_." + bpy.context.space_data.node_tree.search_variables[self.search_value].name + "_array)-1, ", node_data["input_data"][1]["code"], ")"]], "indented": []}]
                else:
                    add_text = ["bpy.context.scene.sn_generated_addon_properties_UID_." + bpy.context.space_data.node_tree.search_variables[self.search_value].name + "_array.add().", bpy.context.space_data.node_tree.search_variables[self.search_value].type, " = ", node_data["input_data"][1]["code"]]

                    if self.operation == "end":
                        blocks = [{"lines": [add_text], "indented": []}]
                    elif self.operation == "start":
                        blocks = [{"lines": [add_text, ["bpy.context.scene.sn_generated_addon_properties_UID_." + bpy.context.space_data.node_tree.search_variables[self.search_value].name + "_array.move(len(bpy.context.scene.sn_generated_addon_properties_UID_." + bpy.context.space_data.node_tree.search_variables[self.search_value].name + "_array)-1, 0)"]], "indented": []}]

        return {"blocks": blocks + [{"lines": [[next_code]],"indented": []}], "errors": errors}

