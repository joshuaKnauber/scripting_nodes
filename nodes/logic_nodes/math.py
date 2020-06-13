import bpy
from ...node_sockets import update_socket_autocompile
from ..base_node import SN_ScriptingBaseNode
from ..node_looks import node_colors, node_icons

class SN_UiMathNode(bpy.types.Node, SN_ScriptingBaseNode):
    '''Node for basic math'''
    bl_idname = 'SN_UiMathNode'
    bl_label = "Math"
    bl_icon = node_icons["LOGIC"]

    operation: bpy.props.EnumProperty(
        items=[("+", "Add", "Add numbers"), ("-", "Subtract", "Subtract numbers"),
                ("*", "Multiply", "Multiply Numbers"), ("/", "Divide", "Divide Numbers")],
        name="Operation",
        description="Math operation for this node",
        update = update_socket_autocompile
    )

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["LOGIC"]

        self.inputs.new('SN_NumberSocket', "Value")
        self.inputs.new('SN_NumberSocket', "Value")
        self.outputs.new('SN_NumberSocket', "Value")

    def copy(self, node):
        pass# called when node is copied

    def free(self):
        pass

    def draw_buttons(self, context, layout):
        layout.prop(self,"operation",text="")

    def evaluate(self,output):
        value1 = str(self.inputs[0].value)
        value2 = str(self.inputs[1].value)

        errors = []

        if self.inputs[0].is_linked:
            if self.inputs[0].links[0].from_socket.bl_idname == "SN_NumberSocket":
                value1 = self.inputs[0].links[0].from_socket
            else:
                errors.append("wrong_socket")
        if self.inputs[1].is_linked:
            if self.inputs[1].links[0].from_socket.bl_idname == "SN_NumberSocket":
                value2 = self.inputs[1].links[0].from_socket
            else:
                errors.append("wrong_socket")

        return {"code": ["(" + value1," ",self.operation," ",value2 + ")"],"error":errors}
        
        