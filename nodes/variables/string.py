#SN_StringVariableNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode
from ...node_tree.node_sockets import is_valid_python, make_valid_python


class SN_StringArray(bpy.types.PropertyGroup):

    def get_python_value(self):
        return self.value

    value: bpy.props.StringProperty(default="",name="Value",description="Value of this variable")
    
bpy.utils.register_class(SN_StringArray)


class SN_StringVariableNode(bpy.types.Node, SN_ScriptingBaseNode):
    bl_idname = "SN_StringVariableNode"
    bl_label = "String Variable"
    bl_icon = "DRIVER_TRANSFORM"
    node_color = (0,0.75,0)
    should_be_registered = True

    value: bpy.props.StringProperty(default="",name="Value",description="Value of this variable")

    def update_socket_value(self,context):
        if not is_valid_python(self.var_name,True):
            self.var_name = make_valid_python(self.var_name,True)
    
    var_name: bpy.props.StringProperty(name="Name",description="Name of this variable",update=update_socket_value)
    
    description: bpy.props.StringProperty(name="Description",description="Description of this variable")

    is_array: bpy.props.BoolProperty(default=False,name="Make Array",description="Allows you to add multiple elements of the same type to this variable")

    array_items: bpy.props.CollectionProperty(type=SN_StringArray)

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
