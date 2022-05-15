import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_TextSizeNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_TextSizeNode"
    bl_label = "Modal Text Size"

    def on_create(self, context):
        self.add_string_input("Text").default_value = "My Modal Text"
        self.add_string_input("Font").subtype = "FILE_PATH"
                
        self.add_float_input("Size").default_value = 20
        self.add_integer_input("DPI").default_value = 72
        
        self.add_float_output("Width")
        self.add_float_output("Height")
        
    def draw_node(self, context, layout):        
        for node in self.root_nodes:
            if node.bl_idname == "SN_ModalOperatorNode":
                break
        else:
            row = layout.row()
            row.alert = True
            row.label(text="This node only works with modal operators!", icon="ERROR")
    
    def evaluate(self, context):
        self.code_imperative = f"""
            def get_text_dimensions(text, font, size, dpi):
                font_id = 0
                if font and os.path.exists(font):
                    font_id = blf.load(font)
                if font_id == -1:
                    print("Couldn't load font!")
                else:
                    blf.size(font_id, size, dpi)
                return blf.dimensions(font_id, text)
        """
        
        self.code_import = """
            import blf
            import os
            """
        
        self.outputs["Width"].python_value = f"get_text_dimensions({self.inputs['Text'].python_value}, {self.inputs['Font'].python_value}, {self.inputs['Size'].python_value}, {self.inputs['DPI'].python_value})[0]"
        self.outputs["Height"].python_value = f"get_text_dimensions({self.inputs['Text'].python_value}, {self.inputs['Font'].python_value}, {self.inputs['Size'].python_value}, {self.inputs['DPI'].python_value})[1]"