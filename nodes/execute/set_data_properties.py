#SN_SetDataPropertiesNode

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

class SN_SetDataPropertiesNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_SetDataPropertiesNode"
    bl_label = "Set Object Data Properties"
    bl_icon = "MESH_CUBE"
    node_color = (0.53, 0.55, 0.53)
    bl_width_default = 180
    should_be_registered = False

    def reset_data_type(self, context):
        for inp in self.inputs:
            if inp.bl_idname != "SN_ObjectSocket" and inp.name != "Execute":
                self.inputs.remove(inp)

    search_value: bpy.props.StringProperty(name="Search value", description="")
    search_properties: bpy.props.CollectionProperty(type=SN_SearchPropertyGroup)

    def inititialize(self, context):
        self.sockets.create_input(self,"EXECUTE","Execute")
        self.sockets.create_input(self,"OBJECT","Data block")
        self.sockets.create_output(self,"EXECUTE","Execute")

    def update(self):
        self.update_dynamic(True)
        self.update_dynamic(False)
        for input_socket in self.inputs:
            for link in input_socket.links:
                link.from_node.update()
                
        self.update_socket_connections()
        self.update_vector_sockets()

        if not self.search_value in self.search_properties:
            self.search_value = ""

        filter_attr = {"ENUM": "filter_string", "STRING": "filter_string", "BOOLEAN": "filter_bool", "INT": "filter_int", "FLOAT": "filter_float", "VECTOR": "filter_vector", "COLLECTION": "filter_data_block_collection", "POINTER": "filter_data_block"}
        if len(self.inputs) >= 2:
            if len(self.inputs[1].links) == 1:
                if self.inputs[1].links[0].from_socket.bl_idname == "SN_ObjectSocket":
                    if self.inputs[1].links[0].from_socket.node.bl_idname != "SN_ForLayoutNode":
                        data_type = self.inputs[1].links[0].from_node.data_type(self.inputs[1].links[0].from_socket)
                        if data_type != "":
                            self.search_properties.clear()
                            for prop in eval(data_type).bl_rna.properties:
                                if getattr(bpy.context.scene.sn_properties, filter_attr[prop.type]):
                                    if not prop.name == "RNA" and not prop.type in ["COLLECTION", "POINTER", "ENUM"]:
                                        if not prop.is_readonly:
                                            item = self.search_properties.add()
                                            item.name = prop.name
                                            item.identifier = prop.identifier
                                            item.description = prop.description
                                            item.is_color = prop.subtype == "COLOR"
                                            if not prop.type in ["INT", "FLOAT"]:
                                                item.type = prop.type
                                            else:
                                                if prop.is_array:
                                                    item.type = "VECTOR"
                                                    item.use_four_numbers = prop.array_length == 4
                                                    item.is_color = prop.subtype == COLOR
                                                else:
                                                    item.type = prop.type
                else:
                    self.search_properties.clear()
                    for inp in self.inputs:
                        if inp.bl_idname != "SN_ObjectSocket" and inp.name != "Execute":
                            if not inp.name in self.search_properties:
                                self.inputs.remove(inp)
            else:
                self.search_properties.clear()
                for inp in self.inputs:
                    if inp.bl_idname != "SN_ObjectSocket" and inp.name != "Execute":
                        if not inp.name in self.search_properties:
                            self.inputs.remove(inp)


    def draw_buttons(self, context, layout):
        if len(self.inputs[1].links) == 1:
            if self.inputs[1].links[0].from_socket.bl_idname == "SN_ObjectSocket":
                row = layout.row(align=True)
                row.prop_search(self,"search_value",self,"search_properties",text="")
                row.popover("SN_PT_FilterPanel", text="", icon="FILTER")

                is_existing = False
                for inp in self.inputs:
                    if inp.name == self.search_value:
                        is_existing = True

                if not is_existing and not self.search_value == "":
                    op = row.operator("scripting_nodes.add_scene_data_socket",text="",icon="ADD")
                    op.node_name = self.name
                    op.socket_name = self.search_value
                    op.is_output = False
                    op.use_four_numbers = self.search_properties[self.search_value].use_four_numbers
                    op.is_color = self.search_properties[self.search_value].is_color
                if is_existing:
                    op = row.operator("scripting_nodes.remove_scene_data_socket",text="",icon="REMOVE")
                    op.node_name = self.name
                    op.socket_name = self.search_value


    def evaluate(self, socket, node_data, errors):
        next_code = ""
        if node_data["output_data"][0]["code"]:
            next_code = node_data["output_data"][0]["code"]

        if len(self.inputs[1].links) == 1:
            if self.inputs[1].links[0].from_socket.bl_idname == "SN_ObjectSocket":
                set_blocks = []
                for x, inp in enumerate(self.inputs):
                    if inp.name != "Execute" and inp.bl_idname != "SN_ObjectSocket":
                        set_blocks.append([node_data["input_data"][1]["code"], "." + self.search_properties[inp.name].identifier, " = ", node_data["input_data"][x]["code"]])
                return {"blocks": [{"lines": set_blocks,"indented": []}, {"lines": [[next_code]],"indented": []}],"errors": errors}

        return {"blocks": [{"lines": [],"indented": []}, {"lines": [[next_code]],"indented": []}],"errors": errors}

