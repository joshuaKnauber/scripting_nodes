import bpy
from ...base_node import SN_ScriptingBaseNode



class SN_DrawModalTextNode(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_DrawModalTextNode"
    bl_label = "Draw Text"
    node_color = "PROGRAM"

    def update_use3d(self, context):
        if self.use_3d:
            self.inputs["Position"].size = 3
        else:
            self.inputs["Position"].size = 2
        self._evaluate(context)

    use_3d: bpy.props.BoolProperty(name="Use 3D", default=False, description="Use 3D coordinates", update=update_use3d)

    def on_create(self, context):
        self.add_execute_input()
        self.add_execute_output()
        
        self.add_string_input("Text").default_value = "My Text"
        self.add_string_input("Font").subtype = "FILE_PATH"
        
        inp = self.add_float_vector_input("Text Color")
        inp.subtype = "COLOR_ALPHA"
        inp.default_value = tuple([1]*32)
        
        self.add_float_input("Size").default_value = 20

        self.add_integer_input("Wrap Width").default_value = 0

        inp = self.add_float_vector_input("Position")
        inp.size = 2
        inp.default_value = [1]*32

        self.add_float_input("Rotation")

    def draw_node(self, context, layout):
        layout.prop(self, "use_3d")
    
    def evaluate(self, context):

        position_code = f"x_{self.static_uid}, y_{self.static_uid} = {self.inputs['Position'].python_value}"
        if self.use_3d:
            position_code = f"x_{self.static_uid}, y_{self.static_uid} = location_3d_to_region_2d(bpy.context.region, bpy.context.space_data.region_3d, tuple({self.inputs['Position'].python_value}))"

        self.code = f"""
            font_id = 0
            if {self.inputs["Font"].python_value} and os.path.exists({self.inputs["Font"].python_value}):
                font_id = blf.load({self.inputs["Font"].python_value})
            if font_id == -1:
                print("Couldn't load font!")
            else:
                {self.indent(position_code, 4)}
                blf.position(font_id, x_{self.static_uid}, y_{self.static_uid}, 0)
                blf.size(font_id, {self.inputs["Size"].python_value})
                clr = {self.inputs["Text Color"].python_value}
                blf.color(font_id, clr[0], clr[1], clr[2], clr[3])
                if {self.inputs["Wrap Width"].python_value if "Wrap Width" in self.inputs else "False"}:
                    blf.enable(font_id, blf.WORD_WRAP)
                    blf.word_wrap(font_id, {self.inputs["Wrap Width"].python_value if "Wrap Width" in self.inputs else "0"})
                if {self.inputs["Rotation"].python_value if "Rotation" in self.inputs else "False"}:
                    blf.enable(font_id, blf.ROTATION)
                    blf.rotation(font_id, {self.inputs["Rotation"].python_value if "Rotation" in self.inputs else "0"})
                blf.enable(font_id, blf.WORD_WRAP)
                blf.draw(font_id, {self.inputs["Text"].python_value})
                blf.disable(font_id, blf.ROTATION)
                blf.disable(font_id, blf.WORD_WRAP)
            {self.indent(self.outputs[0].python_value, 3)}
        """
        self.code_import = f"""
            import blf
            import os
            {"from bpy_extras.view3d_utils import location_3d_to_region_2d" if self.use_3d else ""}
            """