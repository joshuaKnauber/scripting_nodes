#SN_BooleanVariableNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode
from ...node_tree.node_sockets import is_valid_python, make_valid_python


class SN_AddBooleanArrayElement(bpy.types.Operator):
    bl_idname = "scripting_nodes.add_boolean_array_element"
    bl_label = "Add Element"
    bl_description = "Adds a element to this array"
    bl_options = {"REGISTER","INTERNAL","UNDO"}

    node_name: bpy.props.StringProperty()

    def execute(self, context):
        context.space_data.node_tree.nodes[self.node_name].array_elements.add()
        return {"FINISHED"}

class SN_RemoveBooleanArrayElement(bpy.types.Operator):
    bl_idname = "scripting_nodes.remove_boolean_array_element"
    bl_label = "Remove Element"
    bl_description = "Removes this element from this array"
    bl_options = {"REGISTER","INTERNAL","UNDO"}

    node_name: bpy.props.StringProperty()
    element_index: bpy.props.IntProperty()

    def execute(self, context):
        context.space_data.node_tree.nodes[self.node_name].array_elements.remove(self.element_index)
        return {"FINISHED"}


class SN_BooleanArray(bpy.types.PropertyGroup):
    value: bpy.props.BoolProperty(default=True,name="Value",description="Value of this variable")
bpy.utils.register_class(SN_BooleanArray)


class SN_BooleanVariableNode(bpy.types.Node, SN_ScriptingBaseNode):
    bl_idname = "SN_BooleanVariableNode"
    bl_label = "Boolean Variable"
    bl_icon = "DRIVER_TRANSFORM"
    node_color = (0.65,0,0)
    register_in_properties = True
    should_be_registered = True

    value: bpy.props.BoolProperty(default=True,name="Value",description="Value of this variable")

    def update_socket_value(self,context):
        if not is_valid_python(self.var_name,True):
            self.var_name = make_valid_python(self.var_name,True)
    
    var_name: bpy.props.StringProperty(name="Name",description="Name of this variable",update=update_socket_value)
    
    description: bpy.props.StringProperty(name="Description",description="Description of this variable")

    is_array: bpy.props.BoolProperty(default=False,name="Make Array",description="Allows you to add multiple elements of the same type to this variable")

    array_elements: bpy.props.CollectionProperty(type=SN_BooleanArray)

    def inititialize(self, context):
        self.update_socket_value(context)

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
            col.prop(self,"value",toggle=True,text=str(self.value))

        layout.prop(self,"is_array")

        if self.is_array:

            for array_index, array_element in enumerate(self.array_elements):
                row = layout.row()
                split = row.split(factor=0.2)
                split.label(text=str(array_index))
                row = split.row()
                row.prop(array_element,"value",toggle=True,text=str(array_element.value))
                op = row.operator("scripting_nodes.remove_boolean_array_element",text="",icon="PANEL_CLOSE",emboss=False)
                op.node_name = self.name
                op.element_index = array_index
            
            layout.operator("scripting_nodes.add_boolean_array_element",icon="ADD").node_name = self.name

    def evaluate(self, socket, input_data, errors):
        blocks = []
        if self.is_array:
            blocks = [{
                "lines": [["class "+self.var_name+"Collection(bpy.types.PropertyGroup):"]],
                "indented": [[self.property_line()]]
            }]
        return {"blocks": blocks, "errors": errors}

    def property_line(self):
        return self.var_name + ": bpy.props.BoolProperty(name=\""+""+"\",description=\""+self.description+"\",default="+str(self.value)+")"

    def property_block(self):
        if not self.is_array:
            return self.property_line()
        else:
            return self.var_name + ": bpy.props.CollectionProperty(type="+self.var_name+"Collection)"

    def get_register_block(self):
        if self.is_array:
            return ["bpy.utils.register_class("+self.var_name+"Collection)"]
        return []

    def get_unregister_block(self):
        if self.is_array:
            return ["bpy.utils.unregister_class("+self.var_name+"Collection)"]
        return []