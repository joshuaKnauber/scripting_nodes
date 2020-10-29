#SN_VectorVariableNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode
from ...node_tree.node_sockets import is_valid_python, make_valid_python
from uuid import uuid4


class SN_VectorArray(bpy.types.PropertyGroup):
    value: bpy.props.FloatVectorProperty(default=(0,0,0),name="Value",description="Value of this variable")
    four_value: bpy.props.FloatVectorProperty(default=(0,0,0,0),size=4,name="Value",description="Value of this variable")

bpy.utils.register_class(SN_VectorArray)


class SN_VectorVariableNode(bpy.types.Node, SN_ScriptingBaseNode):
    bl_idname = "SN_VectorVariableNode"
    bl_label = "Vector Variable"
    bl_icon = "CON_TRANSFORM"
    node_color = (0.6,0.2,0.8)
    should_be_registered = False
    bl_width_default = 200

    docs = {
        "text": ["This node is used to <important>create a vector variable</>."
                ""],
        "python": ["property_name: bpy.props.FloatVectorProperty(name=<string>\"My Property\"</>, description=<string>\"My description\"</>)"]

    }

    value: bpy.props.FloatVectorProperty(default=(0,0,0),name="Value",description="Value of this variable")
    four_value: bpy.props.FloatVectorProperty(default=(0,0,0,0),size=4,name="Value",description="Value of this variable")

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
        if self.is_array:
            self.outputs.remove(self.outputs[0])
        else:
            self.sockets.create_output(self, "EXECUTE", "Update")
        for item in bpy.context.space_data.node_tree.search_variables:
            if item.name == self.groupItem:
                item.is_array = self.is_array
        identifiers = ["SN_GetVariableNode", "SN_SetVariableNode", "SN_AddToArrayVariableNode", "SN_RemoveFromArrayVariableNode"]
        for node in bpy.context.space_data.node_tree.nodes:
            if node.bl_idname in identifiers:
                node.update_outputs(None)

    def update_four(self, context):
        for item in bpy.context.space_data.node_tree.search_variables:
            if item.name == self.groupItem:
                if self.use_four_numbers:
                    item.type = "four_vector"
                else:
                    item.type = "vector"

        identifiers = ["SN_GetVariableNode", "SN_SetVariableNode", "SN_AddToArrayVariableNode", "SN_RemoveFromArrayVariableNode"]
        for node in bpy.context.space_data.node_tree.nodes:
            if node.bl_idname in identifiers:
                node.update_outputs(None)

    groupItem: bpy.props.StringProperty(default="item_name_placeholder")
    
    var_name: bpy.props.StringProperty(name="Name",description="Name of this variable",update=update_socket_value)

    description: bpy.props.StringProperty(name="Description",description="Description of this variable", update=update_description)

    is_array: bpy.props.BoolProperty(default=False,name="Make Array",description="Allows you to add multiple elements of the same type to this variable", update=update_array)

    array_items: bpy.props.CollectionProperty(type=SN_VectorArray)

    use_four_numbers: bpy.props.BoolProperty(default=False,name="Use Four Numbers", update=update_four)

    var_uid: bpy.props.StringProperty()

    def inititialize(self, context):
        self.sockets.create_output(self, "EXECUTE", "Update")
        self.var_uid = uuid4().hex[:10]
        item = bpy.context.space_data.node_tree.search_variables.add()
        self.groupItem = item.name
        item.type = "vector"
        item.socket_type = "VECTOR"
        item.identifier = self.var_uid
        self.update_socket_value(context)

    def copy(self, context):
        self.var_uid = uuid4().hex[:10]
        item = bpy.context.space_data.node_tree.search_variables.add()
        self.groupItem = item.name
        item.type = "vector"
        item.socket_type = "VECTOR"
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
        
        if not self.is_array:
            col = layout.column(align=True)
            col.label(text="Default Value:")
            if self.use_four_numbers:
                col.prop(self,"four_value",text="")
            else:
                col.prop(self,"value",text="")

        layout.prop(self,"use_four_numbers")
        layout.prop(self,"is_array")

        if self.is_array:

            for array_index, array_element in enumerate(self.array_items):
                row = layout.row()
                split = row.split(factor=0.2)
                split.label(text=str(array_index))
                row = split.row()
                col = row.column()
                if self.use_four_numbers:
                    col.prop(array_element,"four_value",text="")
                else:
                    col.prop(array_element,"value",text="")
                op = row.operator("scripting_nodes.remove_variable_array_element",text="",icon="PANEL_CLOSE",emboss=False)
                op.node_name = self.name
                op.element_index = array_index
            
            layout.operator("scripting_nodes.add_variable_array_element",icon="ADD").node_name = self.name

    def evaluate(self, socket, node_data, errors):
        next_code = ""
        if node_data["output_data"][0]["code"]:
            next_code = node_data["output_data"][0]["code"]

        indented = [["pass"]]
        if next_code:
            indented = [["pass"], [next_code]]
            

        blocks = [{"lines": [["def update_" + self.var_name + "(self, context):"]],"indented": indented}]
        return {"blocks": blocks, "errors": errors}

    def get_variable_line(self):
        if not self.is_array:
            if self.use_four_numbers:
                return self.var_name.replace(" ", "_") + ": bpy.props.FloatVectorProperty(name='" + self.var_name + "', description='" + self.description + "', default=(" +str(self.four_value[0])+", "+str(self.four_value[1])+", "+str(self.four_value[2])+", "+str(self.four_value[3])+ "), size=4" + ", update=update_" + self.var_name + ")"
            else:
                return self.var_name.replace(" ", "_") + ": bpy.props.FloatVectorProperty(name='" + self.var_name + "', description='" + self.description + "', default=(" +str(self.value[0])+", "+str(self.value[1])+", "+str(self.value[2])+ ")" + ", update=update_" + self.var_name + ")"
        else:
            return self.var_name.replace(" ", "_") + "_array: bpy.props.CollectionProperty(type=ArrayCollection_UID_)"

    def get_array_line(self):
        register_block = []
        if self.is_array:
            for element in self.array_items:
                if self.use_four_numbers:
                    register_block.append("bpy.context.scene.sn_generated_addon_properties_UID_." + self.var_name.replace(" ", "_") + "_array.add().four_vector = (" + str(element.four_value[0])+", "+str(element.four_value[1])+", "+str(element.four_value[2])+", "+str(element.four_value[3]) + ")")
                else:
                    register_block.append("bpy.context.scene.sn_generated_addon_properties_UID_." + self.var_name.replace(" ", "_") + "_array.add().vector = (" +str(element.value[0])+", "+str(element.value[1])+", "+str(element.value[2])+")")

        return register_block