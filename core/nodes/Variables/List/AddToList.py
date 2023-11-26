import bpy
from ..templates.VariableReferenceTemplate import VariableReferenceTemplate

from ...base_node import SNA_BaseNode
from .....constants import sockets


class SNA_NodeAddToList(SNA_BaseNode, VariableReferenceTemplate, bpy.types.Node):
    bl_idname = "SNA_NodeAddToList"
    bl_label = "Add To List"

    def on_create(self):
        self.add_input(sockets.PROGRAM)
        inp = self.add_input(sockets.ENUM, "Position")
        inp.add_item("APPEND", "End")
        inp.add_item("PREPEND", "Start")
        self.add_input(sockets.DATA, "Value")
        self.add_output(sockets.PROGRAM)
        self.add_output(sockets.LIST)

    def draw_node(self, context: bpy.types.Context, layout: bpy.types.UILayout):
        self.draw_variable_selection(context, layout)

    def generate(self, context, trigger):
        if self.variable.node:
            if self.inputs["Position"].has_next():
                self.code = f"""
                    if {self.inputs["Position"].get_code()} == "APPEND":
                        {self.variable.node.var_name()}.append({self.inputs["Value"].get_code()})
                    elif {self.inputs["Position"].get_code()} == "PREPEND":
                        {self.variable.node.var_name()}.insert(0, {self.inputs["Value"].get_code()})
                    {self.outputs["Program"].get_code(5)}
                """
            else:
                if self.inputs["Position"].value == "APPEND":
                    self.code = f"""
                        {self.variable.node.var_name()}.append({self.inputs["Value"].get_code()})
                        {self.outputs["Program"].get_code(6)}
                    """
                else:
                    self.code = f"""
                        {self.variable.node.var_name()}.insert(0, {self.inputs["Value"].get_code()})
                        {self.outputs["Program"].get_code(6)}
                    """
            self.outputs["List"].code = self.variable.node.var_name()
        else:
            self.code = f"""
                {self.outputs["Program"].get_code(4)}
            """
