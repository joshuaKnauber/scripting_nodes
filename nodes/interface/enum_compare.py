#SN_EnumCompareLayoutNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_EnumSearchPropertyGroup(bpy.types.PropertyGroup):

    name: bpy.props.StringProperty(default="")
    identifier: bpy.props.StringProperty(default="")
    description: bpy.props.StringProperty(default="")

class SN_EnumCompareLayoutNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_EnumCompareLayoutNode"
    bl_label = "Enum Compare (Layout)"
    bl_icon = "LINENUMBERS_ON"
    node_color = (0.89,0.6,0)
    should_be_registered = False

    def reset_data_type(self, context):
        if self.inputs[1].links[0].from_socket.bl_idname == "SN_ObjectSocket":
            self.update()

    def update_name(self, context):
        for out in self.outputs:
            if out.name != "Layout":
                try:
                    self.outputs.remove(out)
                except RuntimeError:
                    pass 
        self.generate_sockets()

    def update_node(self):
        self.sn_enum_property_properties.clear()

        if len(self.inputs) == 2:
            if len(self.inputs[1].links) == 1:
                if self.inputs[1].links[0].from_socket.bl_idname == "SN_ObjectSocket":

                    data_type = self.inputs[1].links[0].from_node.data_type(self.inputs[1].links[0].from_socket)
                    if data_type != "":
                        for prop in eval(data_type).bl_rna.properties:
                            if prop.type == "ENUM":
                                item = self.sn_enum_property_properties.add()
                                item.name = prop.name
                                item.identifier = prop.identifier
                                item.description = prop.description
        
        if self.search_prop == "internal":
            if not self.propName in self.sn_enum_property_properties:
                self.propName = ""
        else:
            if not self.propName in bpy.context.space_data.node_tree.sn_enum_property_properties:
                self.propName = ""

    def generate_sockets(self):
        if self.search_prop == "internal":
            if self.propName in self.sn_enum_property_properties:
                data_type = self.inputs[1].links[0].from_node.data_type(self.inputs[1].links[0].from_socket)
                if data_type != "":
                    for item in eval(data_type + ".bl_rna.properties['" + self.sn_enum_property_properties[self.propName].identifier + "'].enum_items"):
                        self.sockets.create_output(self,"LAYOUT", item.name)

        else:
            if self.propName in bpy.context.space_data.node_tree.sn_enum_property_properties:
                for node in bpy.context.space_data.node_tree.nodes:
                    if node.bl_idname == "SN_EnumVariableNode":
                        if node.var_name == self.propName:
                            for array_item in node.array_items:
                                self.sockets.create_output(self,"LAYOUT", array_item.name)

    def update_enum(self, context):
        if self.search_prop == "internal":
            if len(self.inputs) != 2:
                self.sockets.create_input(self,"OBJECT","Input")
        else:
            for input_socket in self.inputs:
                if input_socket.name != "Execute":
                    self.inputs.remove(input_socket)

    propName: bpy.props.StringProperty(name="Name", description="The name of the property", update=update_name)
    sn_enum_property_properties: bpy.props.CollectionProperty(type=SN_EnumSearchPropertyGroup)
    search_prop: bpy.props.EnumProperty(items=[("internal", "Internal", "Blenders internal properties"), ("custom", "Custom", "Your custom enums")], name="Properties", description="Which properties to display", update=update_enum)

    def inititialize(self,context):
        self.sockets.create_input(self,"LAYOUT","Layout")
        self.sockets.create_input(self,"OBJECT","Input")

    def draw_buttons(self, context, layout):
        layout.prop(self, "search_prop", expand=True)
        if self.search_prop == "internal":
            layout.prop_search(self,"propName",self,"sn_enum_property_properties",text="")

        else:
            layout.prop_search(self,"propName",bpy.context.space_data.node_tree,"sn_enum_property_properties",text="")

            if self.propName in bpy.context.space_data.node_tree.sn_enum_property_properties:
                if bpy.context.space_data.node_tree.sn_enum_property_properties[self.propName].description != "":
                    box = col.box()
                    box.label(text=bpy.context.space_data.node_tree.sn_enum_property_properties[self.propName].description)
            else:
                if len(self.outputs) > 1:
                    for out in self.outputs:
                        if out.name != "Layout":
                            try:
                                self.outputs.remove(out)
                            except RuntimeError:
                                pass
        

    def evaluate(self, socket, node_data, errors):
        if_block = []
        if self.search_prop == "internal":
            if self.inputs[1].is_linked:
                data_type = self.inputs[1].links[0].from_node.data_type(self.inputs[1].links[0].from_socket)
                if data_type != "":
                    data_type = eval(data_type + ".bl_rna.properties['" + self.sn_enum_property_properties[self.propName].identifier + "'].enum_items")
                    for output in self.outputs:
                        if output.is_linked:
                            if output.name != "Layout":
                                if self.propName in self.sn_enum_property_properties:
                                    for item in data_type:
                                        if item.name == output.name:
                                            if_block.append({"lines": [["if ", node_data["input_data"][1]["code"], "." + self.sn_enum_property_properties[self.propName].identifier + " == '" + item.identifier + "':"]],"indented": [[output.links[0].to_socket]]})
        
        else:
            if self.propName in bpy.context.space_data.node_tree.sn_enum_property_properties:
                for output in self.outputs:
                    if output.is_linked:
                        if output.name != "Layout":
                            if_block.append({"lines": [["if bpy.context.scene.sn_generated_addon_properties_UID_." + self.propName.replace(" ", "_") + " == '" + output.name + "':"]],"indented": [[output.links[0].to_socket]]})

        return {
            "blocks": if_block,
            "errors": errors
        }


    def layout_type(self):
        if self.inputs[0].is_linked:
            if self.inputs[0].links[0].from_socket.bl_idname == self.inputs[0].bl_idname:
                return self.inputs[0].links[0].from_socket.node.layout_type()
        return "layout"

