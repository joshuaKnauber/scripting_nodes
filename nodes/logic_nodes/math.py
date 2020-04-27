import bpy
from ..base_node import SN_ScriptingBaseNode
from ..node_looks import node_colors, node_icons

class SN_UiMathNode(bpy.types.Node, SN_ScriptingBaseNode):
    '''Node for basic math'''
    bl_idname = 'SN_UiMathNode'
    bl_label = "Math"
    bl_icon = node_icons["LOGIC"]

    operation: bpy.props.EnumProperty(
        items=[("ADD", "Add", "Add numbers"), ("SUBTRACT", "Subtract", "Subtract numbers"),
                ("MULTIPLY", "Multiply", "Multiply Numbers"), ("DIVIDE", "Divide", "Divide Numbers")],
        name="Operation",
        description="Math operation for this node"
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
        pass# called when node is removed

    def draw_buttons(self, context, layout):
        layout.prop(self,"operation",text="")

    def evaluate(self):
        if self.operation == "ADD":
            print("BEEF")
        elif self.operation == "SUBTRACT":
            print("BEEF")
        elif self.operation == "MULTIPLY":
            print("BEEF")
        elif self.operation == "DIVIDE":
            print("BEEF")