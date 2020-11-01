#SN_FloatVariableNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode
from ...node_tree.node_sockets import is_valid_python, make_valid_python
from uuid import uuid4


class SN_FloatArray(bpy.types.PropertyGroup):
    value: bpy.props.FloatProperty(default=0,name="Value",description="Value of this variable")
    
bpy.utils.register_class(SN_FloatArray)


class SN_FloatVariableNode(bpy.types.Node, SN_ScriptingBaseNode):
    bl_idname = "SN_FloatVariableNode"
    bl_label = "Float Variable"
    bl_icon = "CON_TRANSFORM"
    node_color = (0.23,0.65,0.75)
    should_be_registered = False
    bl_width_default = 200

    docs = {
        "text": ["This node is used to <important>create a float variable</>."
                ""],
        "python": ["property_name: bpy.props.FloatProperty(name=<string>\"My Property\"</>, description=<string>\"My description\"</>, default=<number>0.2</>)"]

    }

    value: bpy.props.FloatProperty(default=0,name="Value",description="Value of this variable")
    min_value: bpy.props.FloatProperty(default=0,name="Min",description="The minimum value of this variable")
    max_value: bpy.props.FloatProperty(default=0,name="Max",description="The maximum value of this variable")

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
            if len(self.outputs):
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

    def update_subtype(self, context):
        for item in bpy.context.space_data.node_tree.search_variables:
            if item.name == self.groupItem:
                item.type = self.subtype

    groupItem: bpy.props.StringProperty(default="item_name_placeholder")
    
    var_name: bpy.props.StringProperty(name="Name",description="Name of this variable",update=update_socket_value)

    description: bpy.props.StringProperty(name="Description",description="Description of this variable", update=update_description)

    use_min: bpy.props.BoolProperty(default=False,name="Use Min",description="Use a minimum value")
    use_max: bpy.props.BoolProperty(default=False,name="Use Max",description="Use a maximum value")

    is_array: bpy.props.BoolProperty(default=False,name="Make Array",description="Allows you to add multiple elements of the same type to this variable", update=update_array)

    array_items: bpy.props.CollectionProperty(type=SN_FloatArray)

    subtype: bpy.props.EnumProperty(items=[("float", "None", "No subtype"), ("float_pixel", "Pixel", ""), ("float_unsigned", "Unsigned", ""), ("float_percentage", "Percentage", ""), ("float_factor", "Factor", ""), ("float_angle", "Angle", ""), ("float_time", "Time", ""), ("float_distance", "Distance", "")], name="Subtype",description="The subtype of this variable", update=update_subtype)

    var_uid: bpy.props.StringProperty()

    def inititialize(self, context):
        self.sockets.create_output(self, "EXECUTE", "Update")
        self.var_uid = uuid4().hex[:10]
        item = bpy.context.space_data.node_tree.search_variables.add()
        self.groupItem = item.name
        item.type = "float"
        item.socket_type = "FLOAT"
        item.identifier = self.var_uid
        self.update_socket_value(context)

    def copy(self, context):
        self.var_uid = uuid4().hex[:10]
        item = bpy.context.space_data.node_tree.search_variables.add()
        self.groupItem = item.name
        item.type = "float"
        item.socket_type = "FLOAT"
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
        col.prop(self, "subtype")

        if not self.is_array:
            col = layout.column(align=True)
            col.label(text="Default Value:")
            col.prop(self,"value",text="")
            split = col.split()
            col = split.column(align=True)
            col.prop(self, "use_min")
            if self.use_min:
                col.prop(self, "min_value")
            col = split.column(align=True)
            col.prop(self, "use_max")
            if self.use_max:
                col.prop(self, "max_value")

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

    def evaluate(self, socket, node_data, errors):
        next_code = ""
        if len(self.outputs):
            if node_data["output_data"][0]["code"]:
                next_code = node_data["output_data"][0]["code"]
        elif not self.is_array:
            errors.append({"title": "To use update re-add this node!", "message": "", "node": self, "fatal": False})


        indented = [["pass"]]
        if next_code:
            indented = [["pass"], [next_code]]
            

        blocks = [{"lines": [["def update_" + self.var_name + "(self, context):"]],"indented": indented}]
        return {"blocks": blocks, "errors": errors}

    def get_variable_line(self):
        if not self.is_array:
            identifiers = {"float": "NONE", "float_pixel": "PIXEL", "float_unsigned": "UNSIGNED", "float_percentage": "PERCENTAGE", "float_factor": "FACTOR", "float_angle": "ANGLE", "float_time": "TIME", "float_distance": "DISTANCE"}
            min_code = ""
            max_code = ""
            if self.use_min:
                min_code = ", min=" + str(self.min_value)
            if self.use_max:
                max_code = ", max=" + str(self.max_value)
            
            if len(self.outputs):
                return self.var_name.replace(" ", "_") + ": bpy.props.FloatProperty(name='" + self.var_name + "', description='" + self.description + "', default=" + str(self.value) + ", subtype='" + identifiers[self.subtype] + "', update=update_" + self.var_name + min_code + max_code + ")"
            else:
                return self.var_name.replace(" ", "_") + ": bpy.props.FloatProperty(name='" + self.var_name + "', description='" + self.description + "', default=" + str(self.value) + ", subtype='" + identifiers[self.subtype] + "'" + min_code + max_code + ")"

        else:
            return self.var_name.replace(" ", "_") + "_array: bpy.props.CollectionProperty(type=ArrayCollection_UID_)"

    def get_array_line(self):
        register_block = []
        if self.is_array:
            for element in self.array_items:
                register_block.append("bpy.context.scene.sn_generated_addon_properties_UID_." + self.var_name.replace(" ", "_") + "_array.add()." + self.subtype + " = " + str(element.value))

        return register_block