#SN_DropdownNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode



class SN_SearchPropertyGroup(bpy.types.PropertyGroup):

    name: bpy.props.StringProperty(name="Name", default="")
    identifier: bpy.props.StringProperty(name="Identifier",default="")
    description: bpy.props.StringProperty(name="Description",default="")


class SN_DropdownNode(bpy.types.Node, SN_ScriptingBaseNode):
    bl_idname = "SN_DropdownNode"
    bl_label = "Dropdown"
    bl_icon = "SORTALPHA"
    node_color = (0.89,0.6,0)
    bl_width_default = 190
    should_be_registered = False

    def reset_data_type(self, context):
        self.search_properties.clear()
        self.update()

    def inititialize(self,context):
        self.sockets.create_input(self,"LAYOUT","Layout")
        self.sockets.create_input(self,"BOOLEAN","Expand")
        self.sockets.create_input(self,"BOOLEAN","Emboss")
        self.sockets.create_input(self,"STRING","Text")
        self.sockets.create_input(self,"OBJECT","Input")

    def update_enum(self, context):
        self.search_properties.clear()
        for inp in self.inputs:
            if not inp.name in ["Layout", "Expand", "Emboss", "Text"]:
                self.inputs.remove(inp)

        if self.search_prop == "internal":
            if not self.search_value in self.search_properties and self.search_value != "":
                self.search_value = ""
            self.sockets.create_input(self,"OBJECT","Input")
        else:
            if not self.search_value in bpy.context.space_data.node_tree.sn_enum_property_properties:
                self.search_value = ""
        self.update()

    def update(self):
        self.update_dynamic(True)
        self.update_dynamic(False)
        for input_socket in self.inputs:
            for link in input_socket.links:
                link.from_node.update()

        self.update_socket_connections()
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
                                if prop.type == "ENUM":
                                    item = self.search_properties.add()
                                    item.name = prop.name
                                    item.identifier = prop.identifier
                                    item.description = prop.description

    search_value: bpy.props.StringProperty(name="Name", description="The name of the property")
    search_properties: bpy.props.CollectionProperty(type=SN_SearchPropertyGroup)
    search_prop: bpy.props.EnumProperty(items=[("internal", "Internal", "Blenders internal properties"), ("custom", "Custom", "Your custom enums")], name="Properties", description="Which properties to display", update=update_enum)

    def draw_buttons(self, context, layout):
        layout.prop(self,"search_prop", expand=True)
        self.draw_icon_chooser(layout)
        if self.search_prop == "internal":
            layout.prop_search(self,"search_value", self, "search_properties", text="")
        else:
            layout.prop_search(self,"search_value", bpy.context.space_data.node_tree, "sn_enum_property_properties", text="")

            if self.search_value in bpy.context.space_data.node_tree.sn_enum_property_properties:
                if bpy.context.space_data.node_tree.sn_enum_property_properties[self.search_value].description != "":
                    box = col.box()
                    box.label(text=bpy.context.space_data.node_tree.sn_enum_property_properties[self.search_value].description)

    def evaluate(self, socket, node_data, errors):
        layout_type = self.inputs[0].links[0].from_node.layout_type()
        icon = self.icon
        if icon:
            icon = f", icon=\"{icon}\""

        if self.search_prop == "internal":
            if self.search_value in self.search_properties:
                return {"blocks": [{"lines": [[layout_type, ".prop(", node_data["input_data"][4]["code"], ", '", self.search_properties[self.search_value].identifier, "', expand=", node_data["input_data"][1]["code"], ", emboss=", node_data["input_data"][2]["code"], ", text=", node_data["input_data"][3]["code"], icon, ")"]],"indented": []}],"errors": errors}
        else:
            if self.search_value in bpy.context.space_data.node_tree.sn_enum_property_properties:
                return {"blocks": [{"lines": [[layout_type, ".prop(bpy.context.scene.sn_generated_addon_properties_UID_", ", '", bpy.context.space_data.node_tree.sn_enum_property_properties[self.search_value].name.replace(" ", "_"), "', expand=", node_data["input_data"][1]["code"], ", emboss=", node_data["input_data"][2]["code"], ", text=", node_data["input_data"][3]["code"], icon, ")"]],"indented": []}],"errors": errors}

        return {"blocks": [{"lines": [],"indented": []}],"errors": errors}

