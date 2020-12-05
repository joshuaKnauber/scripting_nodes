#SN_ChangeVariableByNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_ChangeVariableByNode(bpy.types.Node, SN_ScriptingBaseNode):
    bl_idname = "SN_ChangeVariableByNode"
    bl_label = "Change Variable by"
    bl_icon = "DRIVER_TRANSFORM"
    node_color = (0.2, 0.2, 0.2)
    should_be_registered = False
    bl_width_default = 225

    docs = {
        "text": ["This node is used to <important>change a number variable by  a specific value</>."
                ""],
        "python": ["self.property_name += <number>3</>"]

    }

    def name_change(self, uid, name):
        if uid == self.var_uid:
            self.search_value = name

    def inititialize(self, context):
        self.sockets.create_input(self, "EXECUTE", "Execute")
        self.sockets.create_output(self, "EXECUTE", "Execute")

    def update_outputs(self, context):
        for inp in range(len(self.inputs)-1):
            self.inputs.remove(self.inputs[1])

        if not self.search_value in bpy.context.space_data.node_tree.search_variables:
            self.var_uid = ""
            if self.search_value != "":
                self.search_value = ""
        else:
            self.var_uid = bpy.context.space_data.node_tree.search_variables[self.search_value].identifier
            if "float" in bpy.context.space_data.node_tree.search_variables[self.search_value].type or "int" in bpy.context.space_data.node_tree.search_variables[self.search_value].type:
                self.sockets.create_input(self, bpy.context.space_data.node_tree.search_variables[self.search_value].socket_type, bpy.context.space_data.node_tree.search_variables[self.search_value].name)
                if bpy.context.space_data.node_tree.search_variables[self.search_value].is_array:
                    self.sockets.create_input(self, "INTEGER", "Index").set_value(0)

    search_value: bpy.props.StringProperty(name="Search Value", description="", update=update_outputs)
    operation: bpy.props.EnumProperty(items=[(" += ", "Add", "Add the value to the variable"), (" -= ", "Subtract", "Subtract from the variable")], name="Operation")
    var_uid: bpy.props.StringProperty()

    def draw_buttons(self, context, layout):
        col = layout.column()
        col.scale_y = 1.25
        col.prop_search(self,"search_value", bpy.context.space_data.node_tree, "search_variables", text="")

        if self.search_value in bpy.context.space_data.node_tree.search_variables:
            if bpy.context.space_data.node_tree.search_variables[self.search_value].description != "":
                box = col.box()
                box.label(text=bpy.context.space_data.node_tree.search_variables[self.search_value].description)

            col.row().prop(self, "operation", expand=True)

            if not "float" in bpy.context.space_data.node_tree.search_variables[self.search_value].type and not "int" in bpy.context.space_data.node_tree.search_variables[self.search_value].type:
                box = col.box()
                box.label(text="Please select a float or integer variable")

    def evaluate(self, socket, node_data, errors):
        next_code = ""
        if node_data["output_data"][0]["code"]:
            next_code = node_data["output_data"][0]["code"]

        blocks = [{"lines": [],"indented": []}]
        if self.search_value in node_data["node_tree"].search_variables:
            if "float" in node_data["node_tree"].search_variables[self.search_value].type or "int" in node_data["node_tree"].search_variables[self.search_value].type:
                if node_data["node_tree"].search_variables[self.search_value].is_array:
                    blocks = [{"lines": [["bpy.context.scene.sn_generated_addon_properties_UID_." + node_data["node_tree"].search_variables[self.search_value].name, "[", node_data["input_data"][2]["code"], "]", self.operation, node_data["input_data"][1]["code"]]],"indented": []}]
                else:
                    blocks = [{"lines": [["bpy.context.scene.sn_generated_addon_properties_UID_." + node_data["node_tree"].search_variables[self.search_value].name, self.operation, node_data["input_data"][1]["code"]]],"indented": []}]

            else:
                errors.append({"title": "Wrong variable selected", "message": "You need to select a integer or float variable", "node": self, "fatal": True})
        else:
            errors.append({"title": "No variable selected", "message": "You need to select a variable", "node": self, "fatal": True})


        return {"blocks": blocks + [{"lines": [[next_code]],"indented": []}], "errors": errors}

