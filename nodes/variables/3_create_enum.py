#SN_EnumVariableNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode
from ...node_tree.node_sockets import is_valid_python, make_valid_python
from uuid import uuid4


class SN_AddEnumItem(bpy.types.Operator):
    bl_idname = "scripting_nodes.add_enum_item"
    bl_label = "Add Element"
    bl_description = "Adds an item to this enum"
    bl_options = {"REGISTER","INTERNAL","UNDO"}

    node_name: bpy.props.StringProperty()

    def execute(self, context):
        item = context.space_data.node_tree.nodes[self.node_name].array_items.add()
        item.name = "Item Name"
        return {"FINISHED"}

class SN_RemoveEnumItem(bpy.types.Operator):
    bl_idname = "scripting_nodes.remove_enum_item"
    bl_label = "Remove Element"
    bl_description = "Removes an item from this enum"
    bl_options = {"REGISTER","INTERNAL","UNDO"}

    node_name: bpy.props.StringProperty()
    element_index: bpy.props.IntProperty()

    def execute(self, context):
        context.space_data.node_tree.nodes[self.node_name].array_items.remove(self.element_index)
        return {"FINISHED"}

class SN_StringArray(bpy.types.PropertyGroup):
    name: bpy.props.StringProperty(default="",name="Display Name",description="The name of the enum item")
    description: bpy.props.StringProperty(default="",name="Description",description="Shown when hovering over the enum item")
    
bpy.utils.register_class(SN_StringArray)


class SN_EnumVariableNode(bpy.types.Node, SN_ScriptingBaseNode):
    bl_idname = "SN_EnumVariableNode"
    bl_label = "Enum Variable"
    bl_icon = "COLLAPSEMENU"
    node_color = (0,0.75,0)
    should_be_registered = False
    bl_width_default = 200

    docs = {
        "text": ["This node is used to <important>create a enum variable</>."
                ""],
        "python": ["property_name: bpy.props.EnumProperty(items=[(<string>\"internal\"</>, <string>\"First\"</>, <string>\"Great description!\"</>), (<string>\"internal_two\"</>, <string>\"Second\"</>, <string>\"Other description\"</>)], name=<string>\"My Property\"</>, description=<string>\"My description\"</>)"]

    }

    def update_socket_value(self,context):
        if not is_valid_python(self.var_name,True, can_have_spaces=False):
            self.var_name = make_valid_python(self.var_name,True, can_have_spaces=False)
        
        identifiers = ["SN_BooleanVariableNode", "SN_FloatVariableNode", "SN_IntegerVariableNode", "SN_StringVariableNode", "SN_VectorVariableNode", "SN_EnumVariableNode", "SN_ColorVariableNode"]

        for node in bpy.context.space_data.node_tree.nodes:
            if node.bl_idname in identifiers:
                if not node == self:
                    if self.var_name == node.var_name:
                        self.var_name = "new_" + self.var_name

        for item in bpy.context.space_data.node_tree.search_variables:
            if item.name == self.groupItem:
                self.groupItem = self.var_name
                item.name = self.var_name

        for item in bpy.context.space_data.node_tree.sn_enum_property_properties:
            if item.name == self.enumItem:
                self.enumItem = self.var_name
                item.name = self.var_name
        
        identifiers = ["SN_GetVariableNode", "SN_SetVariableNode", "SN_AddToArrayVariableNode", "SN_RemoveFromArrayVariableNode"]
        for node in bpy.context.space_data.node_tree.nodes:
            if node.bl_idname in identifiers:
                node.name_change(self.var_uid, self.var_name)
        for node in bpy.context.space_data.node_tree.nodes:
            if node.bl_idname in identifiers:
                node.update_outputs(None)

    def update_description(self, context):
        if not is_valid_python(self.description,True, can_be_empty=True):
            self.description = make_valid_python(self.description,True, can_be_empty=True)
    
        for item in bpy.context.space_data.node_tree.search_variables:
            if item.name == self.groupItem:
                item.description = self.description
    
        identifiers = ["SN_GetVariableNode", "SN_SetVariableNode", "SN_AddToArrayVariableNode", "SN_RemoveFromArrayVariableNode"]
        for node in bpy.context.space_data.node_tree.nodes:
            if node.bl_idname in identifiers:
                node.update_outputs(None)

    var_name: bpy.props.StringProperty(name="Name",description="Name of this enum",update=update_socket_value)

    description: bpy.props.StringProperty(name="Description",description="Description of this enum", update=update_description)

    array_items: bpy.props.CollectionProperty(type=SN_StringArray)

    groupItem: bpy.props.StringProperty(default="item_name_placeholder")
    enumItem: bpy.props.StringProperty(default="item_name_placeholder")
    var_uid: bpy.props.StringProperty()

    def inititialize(self, context):
        self.sockets.create_output(self, "EXECUTE", "Update")
        self.var_uid = uuid4().hex[:10]
        item = bpy.context.space_data.node_tree.sn_enum_property_properties.add()
        item.name = self.enumItem
        item = bpy.context.space_data.node_tree.search_variables.add()
        item.name = self.groupItem
        item.type = "enum"
        item.socket_type = "STRING"
        item.identifier = self.var_uid
        self.update_socket_value(context)

    def draw_buttons(self,context,layout):
        col = layout.column(align=True)
        col.label(text="Name:")
        col.prop(self,"var_name",text="")
        col = layout.column(align=True)
        col.label(text="Description:")
        col.prop(self,"description",text="")

        for enum_index, enum_element in enumerate(self.array_items):
            box = layout.box()
            row = box.row()
            op = row.operator("scripting_nodes.remove_enum_item",text="",icon="PANEL_CLOSE",emboss=False)
            op.node_name = self.name
            op.element_index = enum_index
            row.prop(enum_element,"name",text="")
            row = box.row()
            row.prop(enum_element,"description",text="")

        layout.operator("scripting_nodes.add_enum_item",icon="ADD").node_name = self.name

    def copy(self, context):
        self.var_uid = uuid4().hex[:10]
        item = bpy.context.space_data.node_tree.sn_enum_property_properties.add()
        item.name = self.enumItem
        item = bpy.context.space_data.node_tree.search_variables.add()
        item.type = "enum"
        item.socket_type = "STRING"

        item = bpy.context.space_data.node_tree.search_variables.add()
        item.name = self.groupItem
        item.type = "enum"
        item.socket_type = "STRING"
        item.identifier = self.var_uid
        self.update_socket_value(context)

    def free(self):
        for x, item in enumerate(bpy.context.space_data.node_tree.sn_enum_property_properties):
            if item.name == self.enumItem:
                bpy.context.space_data.node_tree.sn_enum_property_properties.remove(x)
        for x, item in enumerate(bpy.context.space_data.node_tree.search_variables):
            if item.name == self.groupItem:
                bpy.context.space_data.node_tree.search_variables.remove(x)

    def evaluate(self, socket, node_data, errors):
        next_code = ""
        if len(self.outputs):
            if node_data["output_data"][0]["code"]:
                next_code = node_data["output_data"][0]["code"]
        else:
            errors.append({"title": "To use update re-add this node!", "message": "", "node": self, "fatal": False})


        indented = [["pass"]]
        if next_code:
            indented = [["pass"], [next_code]]
            

        blocks = [{"lines": [["def update_" + self.var_name + "(self, context):"]],"indented": indented}]
        return {"blocks": blocks, "errors": errors}

    def get_variable_line(self):
        items = []
        for element in self.array_items:
            items.append((element.name, element.name, element.description))
        if len(self.outputs):
            return self.var_name.replace(" ", "_") + ": bpy.props.EnumProperty(items=" + str(items) + ", name='" + self.var_name + "', description='" + self.description + "'" + ", update=update_" + self.var_name + ")"
        else:
            return self.var_name.replace(" ", "_") + ": bpy.props.EnumProperty(items=" + str(items) + ", name='" + self.var_name + "', description='" + self.description + "'" + ")"

