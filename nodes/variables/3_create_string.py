#SN_StringVariableNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode
from ...node_tree.node_sockets import is_valid_python, make_valid_python
from uuid import uuid4


class SN_StringArray(bpy.types.PropertyGroup):
    none: bpy.props.StringProperty(default="",name="Value",description="Value of this variable")
    file_path: bpy.props.StringProperty(default="",name="Value",description="Value of this variable", subtype="FILE_PATH")
    dir_path: bpy.props.StringProperty(default="",name="Value",description="Value of this variable", subtype="DIR_PATH")
  
bpy.utils.register_class(SN_StringArray)


class SN_StringVariableNode(bpy.types.Node, SN_ScriptingBaseNode):
    bl_idname = "SN_StringVariableNode"
    bl_label = "String Variable"
    bl_icon = "CON_TRANSFORM"
    node_color = (0,0.75,0)
    should_be_registered = True

    docs = {
        "text": ["This node is used to <important>create a string variable</>."
                ""],
        "python": ["property_name: bpy.props.StringProperty(name=<string>\"My Property\"</>, description=<string>\"My description\"</>, default=<string>\"Hi\"</>)"]

    }

    none: bpy.props.StringProperty(default="",name="Value",description="Value of this variable")
    file_path: bpy.props.StringProperty(default="",name="Value",description="Value of this variable", subtype="FILE_PATH")
    dir_path: bpy.props.StringProperty(default="",name="Value",description="Value of this variable", subtype="DIR_PATH")

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

    def update_array(self, context):
        for item in bpy.context.space_data.node_tree.search_variables:
            if item.name == self.groupItem:
                item.is_array = self.is_array
        identifiers = ["SN_GetVariableNode", "SN_SetVariableNode", "SN_AddToArrayVariableNode", "SN_RemoveFromArrayVariableNode"]
        for node in bpy.context.space_data.node_tree.nodes:
            if node.bl_idname in identifiers:
                node.update_outputs(None)

    def update_subtype(self, context):
        for item in bpy.context.space_data.node_tree.search_variables:
            if item.name == self.groupItem:
                if self.subtype == "NONE":
                    item.type = "string"
                elif self.subtype == "FILE_PATH":
                    item.type = "string_filepath"
                else:
                    item.type = "string_dirpath"

    groupItem: bpy.props.StringProperty(default="item_name_placeholder")
    
    var_name: bpy.props.StringProperty(name="Name",description="Name of this variable",update=update_socket_value)

    description: bpy.props.StringProperty(name="Description",description="Description of this variable", update=update_description)

    is_array: bpy.props.BoolProperty(default=False,name="Make Array",description="Allows you to add multiple elements of the same type to this variable", update=update_array)

    subtype: bpy.props.EnumProperty(items=[("NONE", "None", "No subtype"), ("FILE_PATH", "Filepath", "A path to a file"), ("DIR_PATH", "Directorypath", "A path to a directory")], name="Subtype",description="The subtype of this variable", update=update_subtype)

    array_items: bpy.props.CollectionProperty(type=SN_StringArray)

    var_uid: bpy.props.StringProperty()

    def inititialize(self, context):
        self.var_uid = uuid4().hex[:10]
        item = bpy.context.space_data.node_tree.search_variables.add()
        self.groupItem = item.name
        item.type = "string"
        item.socket_type = "STRING"
        item.identifier = self.var_uid
        self.update_socket_value(context)

    def copy(self, context):
        self.var_uid = uuid4().hex[:10]
        item = bpy.context.space_data.node_tree.search_variables.add()
        self.groupItem = item.name
        item.type = "string"
        item.socket_type = "STRING"
        item.identifier = self.var_uid
        self.update_socket_value(context)

    def free(self):
        for x, item in enumerate(bpy.context.space_data.node_tree.search_variables):
            if item.name == self.groupItem:
                bpy.context.space_data.node_tree.search_variables.remove(x)

    def draw_buttons(self,context,layout):
        col = layout.column(align=True)
        col.label(text="Name:")
        col.prop(self,"var_name",text="")
        col = layout.column(align=True)
        col.label(text="Description:")
        col.prop(self,"description",text="")
        col.separator()
        col.prop(self, "subtype", expand=True)
        
        if not self.is_array:
            col = layout.column(align=True)
            col.label(text="Default Value:")
            col.prop(self,self.subtype.lower(),text="")

        layout.prop(self,"is_array")

        if self.is_array:

            for array_index, array_element in enumerate(self.array_items):
                row = layout.row()
                split = row.split(factor=0.2)
                split.label(text=str(array_index))
                row = split.row()
                row.prop(array_element,self.subtype.lower(),text="")
                op = row.operator("scripting_nodes.remove_variable_array_element",text="",icon="PANEL_CLOSE",emboss=False)
                op.node_name = self.name
                op.element_index = array_index
            
            layout.operator("scripting_nodes.add_variable_array_element",icon="ADD").node_name = self.name

    def evaluate(self, socket, node_data, errors):
        blocks = []
        return {"blocks": blocks, "errors": errors}

    def get_variable_line(self):
        if not self.is_array:
            subtype = ", subtype='" + self.subtype + "'"
            if self.subtype == "NONE":
                value = self.none
            elif self.subtype == "FILE_PATH":
                value = self.file_path
            else:
                value = self.dir_path

            return self.var_name.replace(" ", "_") + ": bpy.props.StringProperty(name='" + self.var_name + "', description='" + self.description + "', default='" + value + "'" + subtype + ")"
        else:
            return self.var_name.replace(" ", "_") + "_array: bpy.props.CollectionProperty(type=ArrayCollection_UID_)"

    def get_array_line(self):
        register_block = []
        if self.is_array:
            for element in self.array_items:
                if self.subtype == "NONE":
                    register_block.append("bpy.context.scene.sn_generated_addon_properties_UID_." + self.var_name.replace(" ", "_") + "_array.add().string = '" + element.none + "'")
                elif self.subtype == "FILE_PATH":
                    register_block.append("bpy.context.scene.sn_generated_addon_properties_UID_." + self.var_name.replace(" ", "_") + "_array.add().string_filepath = '" + element.file_path + "'")
                else:
                    register_block.append("bpy.context.scene.sn_generated_addon_properties_UID_." + self.var_name.replace(" ", "_") + "_array.add().string_dirpath = '" + element.dir_path + "'")

        return register_block

