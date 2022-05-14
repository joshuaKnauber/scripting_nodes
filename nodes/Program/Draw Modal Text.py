import bpy
from ...utils import normalize_code
from ..base_node import SN_ScriptingBaseNode



class SN_DrawModalTextNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_DrawModalTextNode"
    bl_label = "Draw Modal Text"
    node_color = "PROGRAM"

    def on_create(self, context):
        self.add_execute_input()
        self.add_execute_output()
        self.add_string_input("Text").default_value = "My Modal Text"
        self.add_integer_input("X").default_value = 100
        self.add_integer_input("Y").default_value = 100
        self.add_integer_input("Z").default_value = 0
        self.add_integer_input("Size").default_value = 20
        self.add_integer_input("DPI").default_value = 72
        inp = self.add_float_vector_input("Color")
        inp.subtype = "COLOR_ALPHA"
        
    def draw_node(self, context, layout):        
        for node in self.root_nodes:
            if node.bl_idname == "SN_ModalOperatorNode":
                break
        else:
            row = layout.row()
            row.alert = True
            row.label(text="This node only works with modal operators!", icon="ERROR")
    
    def evaluate(self, context):
        self.code = f"""
            font_id = 0
            blf.position(font_id, {self.inputs["X"].python_value}, {self.inputs["Y"].python_value}, {self.inputs["Z"].python_value})
            blf.size(font_id, {self.inputs["Size"].python_value}, {self.inputs["DPI"].python_value})
            clr = {self.inputs["Color"].python_value}
            blf.color(font_id, clr[0], clr[1], clr[2], clr[3])
            blf.draw(font_id, {self.inputs["Text"].python_value})
            {self.indent(self.outputs[0].python_value, 3)}
        """