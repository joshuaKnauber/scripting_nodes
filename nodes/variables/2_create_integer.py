#SN_IntegerVariableNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode
from ...node_tree.node_sockets import is_valid_python, make_valid_python


class SN_IntegerArray(bpy.types.PropertyGroup):

    def get_python_value(self):
        return str(self.value)

    value: bpy.props.IntProperty(default=0,name="Value",description="Value of this variable")
    
bpy.utils.register_class(SN_IntegerArray)


class SN_IntegerVariableNode(bpy.types.Node, SN_ScriptingBaseNode):
    bl_idname = "SN_IntegerVariableNode"
    bl_label = "Create Integer"
    bl_icon = "DRIVER_TRANSFORM"
    node_color = (0.2,0.4,0.75)
    should_be_registered = True

    value: bpy.props.IntProperty(default=0,name="Value",description="Value of this variable")

    def update_socket_value(self,context):
        if not is_valid_python(self.var_name,True):
            self.var_name = make_valid_python(self.var_name,True)

        indentifiers = ["SN_BooleanVariableNode", "SN_FloatVariableNode", "SN_IntegerVariableNode", "SN_StringVariableNode", "SN_VectorVariableNode", "SN_EnumVariableNode"]

        for node in bpy.context.space_data.node_tree.nodes:
            if node.bl_idname in indentifiers:
                if not node == self:
                    if self.var_name == node.var_name:
                        self.var_name = "new_" + self.var_name

        for item in bpy.context.scene.sn_properties.search_variables:
            if item.name == self.groupItem:
                self.groupItem = self.var_name
                item.name = self.var_name

    def update_description(self, context):
        if not is_valid_python(self.description,True):
            self.description = make_valid_python(self.description,True)
    
        for item in bpy.context.scene.sn_properties.search_variables:
            if item.name == self.groupItem:
                item.description = self.description
        identifiers = ["SN_GetVariableNode"]
        for node in bpy.context.space_data.node_tree.nodes:
            if node.bl_idname in identifiers:
                node.update_outputs(None)

    def update_array(self, context):
        for item in bpy.context.scene.sn_properties.search_variables:
            if item.name == self.groupItem:
                item.is_array = self.is_array
        identifiers = ["SN_GetVariableNode"]
        for node in bpy.context.space_data.node_tree.nodes:
            if node.bl_idname in identifiers:
                node.update_outputs(None)

    groupItem: bpy.props.StringProperty(default="item_name_placeholder")
    
    var_name: bpy.props.StringProperty(name="Name",description="Name of this variable",update=update_socket_value)

    description: bpy.props.StringProperty(name="Description",description="Description of this variable", update=update_description)

    is_array: bpy.props.BoolProperty(default=False,name="Make Array",description="Allows you to add multiple elements of the same type to this variable", update=update_array)

    array_items: bpy.props.CollectionProperty(type=SN_IntegerArray)

    def inititialize(self, context):
        global groupItem
        item = bpy.context.scene.sn_properties.search_variables.add()
        self.groupItem = item.name
        for item in bpy.context.scene.sn_properties.search_variables:
            if item.name == self.groupItem:
                item.type = "int"
                item.socket_type = "INTEGER"
        self.update_socket_value(context)

    def free(self):
        for x, item in enumerate(bpy.context.scene.sn_properties.search_variables):
            if item.name == self.groupItem:
                bpy.context.scene.sn_properties.search_variables.remove(x)

    def draw_buttons(self,context,layout):
        col = layout.column(align=True)
        col.label(text="Name:")
        col.prop(self,"var_name",text="")
        col = layout.column(align=True)
        col.label(text="Description:")
        col.prop(self,"description",text="")
        
        if not self.is_array:
            col = layout.column(align=True)
            col.label(text="Default Value:")
            col.prop(self,"value",text="")

        layout.prop(self,"is_array")

        if self.is_array:

            for array_index, array_element in enumerate(self.array_items):
                row = layout.row()
                split = row.split(factor=0.2)
                split.label(text=str(array_index))
                row = split.row()
                row.prop(array_element,"value",text="")
                op = row.operator("scripting_nodes.remove_variable_array_element",text="",icon="PANEL_CLOSE",emboss=False)
                op.node_name = self.name
                op.element_index = array_index
            
            layout.operator("scripting_nodes.add_variable_array_element",icon="ADD").node_name = self.name

    def evaluate(self, socket, input_data, errors):
        blocks = []
        return {"blocks": blocks, "errors": errors}

    def get_variable_line(self):
        if not self.is_array:
            return self.var_name.replace(" ", "_") + ": bpy.props.IntProperty(name='" + self.var_name + "', description='" + self.description + "', default=" + str(self.value) + ")"
        else:
            return self.var_name.replace(" ", "_") + "_array: bpy.props.CollectionProperty(type=ArrayCollection_UID_)"

    def get_array_line(self):
        register_block = []
        if self.is_array:
            for element in self.array_items:
                register_block.append("bpy.context.scene.sn_generated_addon_properties_UID_." + self.var_name.replace(" ", "_") + "_array.add().int = " + str(element.value))

        return register_block