#SN_CheckboxNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode



class SN_SearchPropertyGroup(bpy.types.PropertyGroup):

    name: bpy.props.StringProperty(name="Name", default="")
    identifier: bpy.props.StringProperty(name="Identifier",default="")
    description: bpy.props.StringProperty(name="Description",default="")


class SN_CheckboxNode(bpy.types.Node, SN_ScriptingBaseNode):
    bl_idname = "SN_CheckboxNode"
    bl_label = "Display Checkbox"
    bl_icon = "CON_TRANSFORM"
    node_color = (0.89,0.6,0)
    bl_width_default = 190
    should_be_registered = False

    docs = {
        "text": ["The checkbox can add <important>checkboxes and toggles</> to your interface.",
                "",
                "Internal/Custom: <subtext>Internal uses the Input Socket while custom is looking for Boolean variables in your nodes</>",
                "                           <subtext>You can select the property from the search below this</>",
                "Toggle: <subtext>If the input should be a toggle or a checkbox</>",
                "Emboss: <subtext>If the input should have an embossed look</>",
                "Text: <subtext>The text that will be shown on the input</>",
                "Input: <subtext>The object data that contains the boolean property</>"],
        "python": ["layout.<function>prop</>(data, <string>\"boolean_property\"</>, text=<string>\"My input text\"</>)"]
    }

    def reset_data_type(self, context):
        self.search_properties.clear()
        self.update()

    def inititialize(self,context):
        self.sockets.create_input(self,"LAYOUT","Layout")
        self.sockets.create_input(self,"BOOLEAN","Toggle")
        self.sockets.create_input(self,"BOOLEAN","Emboss")
        self.sockets.create_input(self,"STRING","Text")

        self.sockets.create_input(self,"OBJECT","Input")

    def update_name(self, context):
        if self.search_prop == "custom":
            if self.search_value in bpy.context.space_data.node_tree.search_variables:
                if bpy.context.space_data.node_tree.search_variables[self.search_value].type == "bool":
                    if bpy.context.space_data.node_tree.search_variables[self.search_value].is_array:
                        if len(self.inputs) == 5:
                            if self.inputs[4].name != "Index":
                                self.inputs.remove(self.inputs[4])
                                self.sockets.create_input(self,"INTEGER","Index").set_value(0)
                        else:
                            self.sockets.create_input(self,"INTEGER","Index").set_value(0)
                    else:
                        for inp in self.inputs:
                            if not inp.name in ["Layout", "Toggle", "Emboss", "Text"]:
                                self.inputs.remove(inp)
                else:
                    for inp in self.inputs:
                        if not inp.name in ["Layout", "Toggle", "Emboss", "Text"]:
                            self.inputs.remove(inp)
            else:
                for inp in self.inputs:
                    if not inp.name in ["Layout", "Toggle", "Emboss", "Text"]:
                        self.inputs.remove(inp)
        else:
            if not self.search_value in self.search_properties and self.search_value != "":
                self.search_value = ""

    def update_enum(self, context):
        self.search_properties.clear()
        if len(self.inputs) == 5:
            for inp in self.inputs:
                if not inp.name in ["Layout", "Toggle", "Emboss", "Text"]:
                    self.inputs.remove(inp)

        if self.search_prop == "internal":
            if not self.search_value in self.search_properties and self.search_value != "":
                self.search_value = ""
            self.sockets.create_input(self,"OBJECT","Input")
        else:
            if not self.search_value in bpy.context.space_data.node_tree.search_variables:
                self.search_value = ""
        self.update()

    def update_node(self):
        if self.search_prop == "internal":
            if not self.search_value in self.search_properties:
                self.search_value = ""
            if len(self.inputs) == 5:
                self.search_properties.clear()
                if len(self.inputs[4].links) == 1:
                    if self.inputs[4].links[0].from_socket.bl_idname == "SN_ObjectSocket":
                        data_type = self.inputs[4].links[0].from_node.data_type(self.inputs[4].links[0].from_socket)
                        if data_type != "":
                            for prop in eval(data_type).bl_rna.properties:
                                if prop.type == "BOOLEAN":
                                    item = self.search_properties.add()
                                    item.name = prop.name
                                    item.identifier = prop.identifier
                                    item.description = prop.description

    search_value: bpy.props.StringProperty(name="Name", description="The name of the property", update=update_name)
    search_properties: bpy.props.CollectionProperty(type=SN_SearchPropertyGroup)
    search_prop: bpy.props.EnumProperty(items=[("internal", "Internal", "Blenders internal properties"), ("custom", "Custom", "Your custom booleans")], name="Properties", description="Which properties to display", update=update_enum)

    def draw_buttons(self, context, layout):
        layout.prop(self,"search_prop", expand=True)
        self.draw_icon_chooser(layout)
        if self.search_prop == "internal":
            layout.prop_search(self,"search_value", self, "search_properties", text="")
        else:
            layout.prop_search(self,"search_value", bpy.context.space_data.node_tree, "search_variables", text="")

            if self.search_value in bpy.context.space_data.node_tree.search_variables:
                if bpy.context.space_data.node_tree.search_variables[self.search_value].type == "bool":
                    if bpy.context.space_data.node_tree.search_variables[self.search_value].description != "":
                        box = layout.box()
                        box.label(text=bpy.context.space_data.node_tree.search_variables[self.search_value].description)

                    if bpy.context.space_data.node_tree.search_variables[self.search_value].is_array:
                        if len(self.inputs) != 5:
                            self.update_name(None)
                    else:
                        if len(self.inputs) == 5:
                            self.inputs.remove(self.inputs[4])
                else:
                    box = layout.box()
                    box.label(text="Please select a boolean variable")


    def evaluate(self, socket, node_data, errors):
        layout_type = self.inputs[0].links[0].from_node.layout_type()
        icon = self.icon
        if icon:
            icon = f", icon=\"{icon}\""

        if self.search_prop == "internal":
            if self.search_value in self.search_properties:
                return {"blocks": [{"lines": [[layout_type, ".prop(", node_data["input_data"][4]["code"], ", '", self.search_properties[self.search_value].identifier, "', toggle=", node_data["input_data"][1]["code"], ", emboss=", node_data["input_data"][2]["code"], ", text=", node_data["input_data"][3]["code"], icon, ")"]],"indented": []}],"errors": errors}
            else:
                errors.append({"title": "No variable selected", "message": "You need to select the variable you want to display", "node": self, "fatal": True})
                return {"blocks": [{"lines": [],"indented": []}],"errors": errors}
        else:
            if self.search_value in node_data["node_tree"].search_variables:
                if node_data["node_tree"].search_variables[self.search_value].type == "bool":
                    if len(self.inputs) == 5:
                        return {"blocks": [{"lines": [[layout_type, ".prop(bpy.context.scene.sn_generated_addon_properties_UID_.", node_data["node_tree"].search_variables[self.search_value].name.replace(" ", "_"), "_array[", node_data["input_data"][4]["code"], "], '", node_data["node_tree"].search_variables[self.search_value].type, "', toggle=", node_data["input_data"][1]["code"], ", emboss=", node_data["input_data"][2]["code"], ", text=", node_data["input_data"][3]["code"], icon, ")"]],"indented": []}],"errors": errors}
                    else:
                        return {"blocks": [{"lines": [[layout_type, ".prop(bpy.context.scene.sn_generated_addon_properties_UID_, '", node_data["node_tree"].search_variables[self.search_value].name.replace(" ", "_"), "', toggle=", node_data["input_data"][1]["code"], ", emboss=", node_data["input_data"][2]["code"], ", text=", node_data["input_data"][3]["code"], icon, ")"]],"indented": []}],"errors": errors}
                else:
                    errors.append({"title": "Wrong variable selected", "message": "You need to select a boolean variable", "node": self, "fatal": True})
                    return {"blocks": [{"lines": [],"indented": []}],"errors": errors}

            else:
                errors.append({"title": "No variable selected", "message": "You need to select the variable you want to display", "node": self, "fatal": True})
                return {"blocks": [{"lines": [],"indented": []}],"errors": errors}

        return {"blocks": [{"lines": [],"indented": []}],"errors": errors}

