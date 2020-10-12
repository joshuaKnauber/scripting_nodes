#SN_GetDataPropertiesNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_SearchPropertyGroup(bpy.types.PropertyGroup):

    name: bpy.props.StringProperty(name="Name", default="")
    identifier: bpy.props.StringProperty(name="Identifier",default="")
    description: bpy.props.StringProperty(name="Description",default="")
    type: bpy.props.StringProperty(name="Type",default="")
    use_four_numbers: bpy.props.BoolProperty()
    is_color: bpy.props.BoolProperty(default=False)

class SN_PT_FilterPanel(bpy.types.Panel):
    bl_space_type = 'NODE_EDITOR'
    bl_region_type = 'WINDOW'
    bl_label = "Filter"
    bl_width = 150
    bl_ui_units_x = 6

    def draw(self, context):
        layout = self.layout

        layout.label(text="Data Types:")
        row = layout.row(align=True)
        
        row.prop(context.scene.sn_properties, "filter_string", icon="SORTALPHA", text="")
        row.prop(context.scene.sn_properties, "filter_bool", icon="FORCE_CHARGE", text="")
        row.prop(context.scene.sn_properties, "filter_int", icon="CON_TRANSFORM", text="")
        row.prop(context.scene.sn_properties, "filter_float", icon="CON_TRANSFORM", text="")
        row.prop(context.scene.sn_properties, "filter_vector", icon="CON_TRANSFORM", text="")
        row.prop(context.scene.sn_properties, "filter_data_block_collection", icon="OUTLINER_OB_GROUP_INSTANCE", text="")
        row.prop(context.scene.sn_properties, "filter_data_block", icon="MESH_CUBE", text="")

class SN_GetDataPropertiesNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_GetDataPropertiesNode"
    bl_label = "Get Object Data Properties"
    bl_icon = "MESH_CUBE"
    node_color = (0.53, 0.55, 0.53)
    bl_width_default = 180
    should_be_registered = False

    docs = {
        "text": ["This node is used for <important>getting the properties of objects or controlling collections</>.",
                "Object Input: Changes to data block input, used to select the object or data block you want to use",
                ""],
        "python": ["bpy.data.objects[<string>'Cube'</>].active_material"]

    }


    def update_index(self, context):
        for inp in self.inputs:
            if inp.bl_idname != "SN_CollectionSocket" and inp.bl_idname != "SN_ObjectSocket":
                self.inputs.remove(inp)

        if self.use_index:
            self.sockets.create_input(self,"INTEGER","Index").set_value(0)
        else:
            self.sockets.create_input(self,"STRING","Name")

    def reset_data_type(self, context):
        self.search_value = ""
        if self.inputs[0].links[0].from_socket.bl_idname == "SN_CollectionSocket":
            if self.outputs[0].is_linked:
                if self.outputs[0].links[0].to_socket.bl_idname in ["SN_CollectionSocket", "SN_ObjectSocket"]:
                    self.outputs[0].links[0].to_node.reset_data_type(None)
                else:
                    self.update()

        elif self.inputs[0].links[0].from_socket.bl_idname == "SN_ObjectSocket":
            self.update()
            for out in self.outputs:
                if not out.name in self.search_properties:
                    self.outputs.remove(out)

            for out in self.outputs:
                if out.bl_idname in ["SN_CollectionSocket", "SN_ObjectSocket"]:
                    if out.is_linked:
                        out.links[0].to_node.reset_data_type(None)
            self.update()

    search_value: bpy.props.StringProperty(name="Search value", description="")
    search_properties: bpy.props.CollectionProperty(type=SN_SearchPropertyGroup)
    use_index: bpy.props.BoolProperty(name="Use Index", description="Use Index instead of name", default=True, update=update_index)

    def inititialize(self,context):
        self.sockets.create_input(self,"OBJECT","Object or data block")

    def update(self):
        self.update_dynamic(True)
        self.update_dynamic(False)
        for input_socket in self.inputs:
            for link in input_socket.links:
                link.from_node.update()

        if not self.search_value in self.search_properties:
            self.search_value = ""
        filter_attr = {"ENUM": "filter_string", "STRING": "filter_string", "BOOLEAN": "filter_bool", "INT": "filter_int", "FLOAT": "filter_float", "VECTOR": "filter_vector", "COLLECTION": "filter_data_block_collection", "POINTER": "filter_data_block"}
        if len(self.inputs[0].links) == 1:
            if self.inputs[0].links[0].from_socket.bl_idname == "SN_ObjectSocket":
                if not self.inputs[0].bl_idname == "SN_ObjectSocket":
                    self.sockets.change_socket_type(self, self.inputs[0], "OBJECT")

                self.search_properties.clear()
                data_type = self.inputs[0].links[0].from_node.data_type(self.inputs[0].links[0].from_socket)
                if data_type != "":
                    for prop in eval(data_type).bl_rna.properties:
                        if getattr(bpy.context.scene.sn_properties, filter_attr[prop.type]):
                            if not prop.name == "RNA":
                                item = self.search_properties.add()
                                item.name = prop.name
                                item.identifier = prop.identifier
                                item.description = prop.description
                                if not prop.type in ["INT", "FLOAT"]:
                                    item.type = prop.type
                                else:
                                    if prop.is_array:
                                        item.type = "VECTOR"
                                        item.use_four_numbers = prop.array_length == 4
                                        item.is_color = prop.name == "Color"
                                        # item.is_color = prop.subtype == "COLOR"
                                    else:
                                        item.type = prop.type

            elif self.inputs[0].links[0].from_socket.bl_idname == "SN_CollectionSocket":
                if not self.inputs[0].bl_idname == "SN_CollectionSocket":
                    self.sockets.change_socket_type(self, self.inputs[0], "COLLECTION")

                if not len(self.outputs) == 3:
                    self.sockets.create_output(self,"OBJECT","Element")
                    self.sockets.create_output(self,"INTEGER","Length")
                    self.sockets.create_output(self,"BOOLEAN","Existing")
                if not len(self.inputs) == 2:
                    self.update_index(None)

        else:
            for out in self.outputs:
                self.outputs.remove(out)
            for inp in self.inputs:
                if inp.bl_idname != "SN_CollectionSocket" and inp.bl_idname != "SN_ObjectSocket":
                    self.inputs.remove(inp)

        self.update_socket_connections()
        self.update_vector_sockets()


    def draw_buttons(self, context, layout):
        if len(self.inputs[0].links) == 1:
            if self.inputs[0].links[0].from_socket.bl_idname == "SN_CollectionSocket":
                data_type = self.inputs[0].links[0].from_node.data_type(self.inputs[0].links[0].from_socket)
                if data_type != "":
                    box = layout.box()
                    box.label(text=eval(data_type).bl_rna.name)
                layout.prop(self, "use_index")

            elif self.inputs[0].links[0].from_socket.bl_idname == "SN_ObjectSocket":
                row = layout.row(align=True)
                row.prop_search(self,"search_value",self,"search_properties",text="")
                row.popover("SN_PT_FilterPanel", text="", icon="FILTER")

                is_existing = False
                for out in self.outputs:
                    if out.name == self.search_value:
                        is_existing = True
                for inp in self.inputs:
                    if inp.name == self.search_value:
                        is_existing = True

                if self.search_value == "":
                    op = row.operator("scripting_nodes.add_custom_socket",text="",icon="ADD")
                    op.node_name = self.name
                    op.is_output = True

                if not is_existing and not self.search_value == "":
                    op = row.operator("scripting_nodes.add_scene_data_socket",text="",icon="ADD")
                    op.node_name = self.name
                    op.socket_name = self.search_value
                    op.is_output = True
                    op.use_four_numbers = self.search_properties[self.search_value].use_four_numbers
                    op.is_color = self.search_properties[self.search_value].is_color
                if is_existing:
                    op = row.operator("scripting_nodes.remove_scene_data_socket",text="",icon="REMOVE")
                    op.node_name = self.name
                    op.socket_name = self.search_value


    def evaluate(self, socket, node_data, errors):
        if len(self.inputs[0].links) == 1:
            if self.inputs[0].links[0].from_socket.bl_idname == "SN_CollectionSocket":
                if socket == self.outputs[0]:
                    index = node_data["input_data"][1]["code"]
                    return {"blocks": [{"lines": [[node_data["input_data"][0]["code"], "[", index, "]"]],"indented": []}],"errors": errors}
                elif socket == self.outputs[1]:
                    return {"blocks": [{"lines": [["len(", node_data["input_data"][0]["code"], ")"]],"indented": []}],"errors": errors}
                elif socket == self.outputs[2]:
                    return {"blocks": [{"lines": [["len(", node_data["input_data"][0]["code"], ") != 0"]],"indented": []}],"errors": errors}

            elif self.inputs[0].links[0].from_socket.bl_idname == "SN_ObjectSocket":
                if socket.name in self.search_properties:
                    if self.search_properties[socket.name].type != "ENUM":
                        return {"blocks": [{"lines": [[node_data["input_data"][0]["code"], "." + self.search_properties[socket.name].identifier]],"indented": []}],"errors": errors}
                    else:
                        return {"blocks": [{"lines": [[node_data["input_data"][0]["code"], ".bl_rna.properties['" + self.search_properties[socket.name].identifier + "'].enum_items[", node_data["input_data"][0]["code"], "." + self.search_properties[socket.name].identifier + "].name"]],"indented": []}],"errors": errors}
                else:
                    return {"blocks": [{"lines": [[node_data["input_data"][0]["code"], "." + socket.name]],"indented": []}],"errors": errors}

        return {"blocks": [{"lines": [],"indented": []}],"errors": errors}

    def data_type(self, output):
        if len(self.inputs[0].links) == 1:
            data_type = self.inputs[0].links[0].from_node.data_type(self.inputs[0].links[0].from_socket)
            if data_type != "":
                if self.inputs[0].links[0].from_socket.bl_idname == "SN_CollectionSocket":
                    return "bpy.types." + eval(data_type).bl_rna.identifier

                elif self.inputs[0].links[0].from_socket.bl_idname == "SN_ObjectSocket":
                    for prop in eval(data_type).bl_rna.properties:
                        if prop.name == output.name:
                            return "bpy.types." + eval(data_type).bl_rna.properties[prop.identifier].fixed_type.identifier

        return ""
