import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode
from ...node_tree.node_sockets import is_valid_python, make_valid_python


class SN_BooleanVariableNode(bpy.types.Node, SN_ScriptingBaseNode):
    bl_idname = "SN_BooleanVariableNode"
    bl_label = "Boolean Variable"
    bl_icon = "DRIVER_TRANSFORM"
    node_color = (0.65,0,0)
    should_be_registered = True

    value: bpy.props.BoolProperty(default=True,name="Value",description="Value of this variable")

    def update_socket_value(self,context):
        if not is_valid_python(self.name,True):
            self.name = make_valid_python(self.name,True)
    
    name: bpy.props.StringProperty(name="Name",description="Name of this variable",update=update_socket_value)

    def inititialize(self, context):
        self.update_socket_value(context)

    def draw_buttons(self,context,layout):
        layout.prop(self,"name",text="")
        layout.prop(self,"value",toggle=True,text=str(self.value))

    def evaluate(self, socket, input_data, errors):
        return {"blocks": [], "errors": errors}

    def get_register_block(self):
        return ["pass #test"]

    def get_unregister_block(self):
        return ["pass #test"]