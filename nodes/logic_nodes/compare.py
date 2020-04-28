import bpy
from ..base_node import SN_ScriptingBaseNode
from ..node_looks import node_colors, node_icons

class SN_CompareNode(bpy.types.Node, SN_ScriptingBaseNode):
    '''Node for comparing two values'''
    bl_idname = 'SN_CompareNode'
    bl_label = "Compare"
    bl_icon = node_icons["LOGIC"]

    operation: bpy.props.EnumProperty(
        items=[("==", "=", "Equal to"), ("!=", "≠", "Not equal to"),
                (">", ">", "Bigger than"), ("<", "<", "Smaller than"),
                (">=", "≥", "Bigger or equal to"), ("<=", "≤", "Smaller or equal to")],
        name="Operation",
        description="Compare operation for this node"
    )

    def init(self, context):
        self.use_custom_color = True
        self.color = node_colors["LOGIC"]

        self.inputs.new('SN_NumberSocket', "Value")
        self.inputs.new('SN_NumberSocket', "Value")
        self.outputs.new('SN_BooleanSocket', "Output")

    def copy(self, node):
        pass# called when node is copied

    def free(self):
        pass

    def draw_buttons(self, context, layout):
        layout.prop(self,"operation",text="")

    def evaluate(self,output):
        value1 = str(self.inputs[0].value)
        value2 = str(self.inputs[1].value)

        if self.inputs[0].is_linked:
            value1 = self.inputs[0].links[0].from_socket
        if self.inputs[1].is_linked:
            value2 = self.inputs[1].links[0].from_socket

        if self.outputs[0].is_linked:
            return {"code": [value1, " ", self.operation, " ", value2]}
        else:
            return {"code": [], "error": 2}