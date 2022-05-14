import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_DrawModalTextNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_DrawModalTextNode"
    bl_label = "Draw Modal Text"
    node_color = "PROGRAM"

    def on_create(self, context):
        self.add_execute_input()
        self.add_execute_output()
        
        self.add_string_input("Text").default_value = "My Modal Text"
        self.add_string_input("Font").subtype = "FILE_PATH"
        
        inp = self.add_float_vector_input("Text Color")
        inp.subtype = "COLOR_ALPHA"
        inp.default_value = tuple([1]*32)
        
        self.add_float_input("Size").default_value = 20
        self.add_integer_input("DPI").default_value = 72

        inp = self.add_integer_vector_input("Position")
        inp.size = 2
        inp.default_value = [100]*32
        self.add_integer_input("Z").default_value = 0
        
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
            if {self.inputs["Font"].python_value} and os.path.exists({self.inputs["Font"].python_value}):
                font_id = blf.load({self.inputs["Font"].python_value})
            if font_id == -1:
                print("Couldn't load font!")
            else:
                blf.position(font_id, {self.inputs["Position"].python_value}[0], {self.inputs["Position"].python_value}[1], {self.inputs["Z"].python_value})
                blf.size(font_id, {self.inputs["Size"].python_value}, {self.inputs["DPI"].python_value})
                clr = {self.inputs["Text Color"].python_value}
                blf.color(font_id, clr[0], clr[1], clr[2], clr[3])
                blf.draw(font_id, {self.inputs["Text"].python_value})
            {self.indent(self.outputs[0].python_value, 3)}
        """
        self.code_import = "import os"