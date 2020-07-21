#SN_VectorVariableNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode
from ...node_tree.node_sockets import is_valid_python, make_valid_python


class SN_VectorArray(bpy.types.PropertyGroup):

    def get_python_value(self):
        return str(self.value)#TODO: return four_value if needed

    value: bpy.props.FloatVectorProperty(default=(0,0,0),name="Value",description="Value of this variable")
    four_value: bpy.props.FloatVectorProperty(default=(0,0,0,0),size=4,name="Value",description="Value of this variable")

bpy.utils.register_class(SN_VectorArray)


class SN_VectorVariableNode(bpy.types.Node, SN_ScriptingBaseNode):
    bl_idname = "SN_VectorVariableNode"
    bl_label = "Create Vector"
    bl_icon = "DRIVER_TRANSFORM"
    node_color = (0.6,0.2,0.8)
    should_be_registered = True

    value: bpy.props.FloatVectorProperty(default=(0,0,0),name="Value",description="Value of this variable")
    four_value: bpy.props.FloatVectorProperty(default=(0,0,0,0),size=4,name="Value",description="Value of this variable")

    def update_socket_value(self,context):
        if not is_valid_python(self.var_name,True):
            self.var_name = make_valid_python(self.var_name,True)
    
    var_name: bpy.props.StringProperty(name="Name",description="Name of this variable",update=update_socket_value)
    
    description: bpy.props.StringProperty(name="Description",description="Description of this variable")

    is_array: bpy.props.BoolProperty(default=False,name="Make Array",description="Allows you to add multiple elements of the same type to this variable")

    array_items: bpy.props.CollectionProperty(type=SN_VectorArray)

    use_four_numbers: bpy.props.BoolProperty(default=False,name="Use Four Numbers")

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

    def evaluate(self, socket, input_data, errors):
        blocks = []
        return {"blocks": blocks, "errors": errors}
