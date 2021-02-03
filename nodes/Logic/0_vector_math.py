import bpy
import string
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_VectorMathNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_VectorMathNode"
    bl_label = "Vector Math"
    # bl_icon = "GRAPH"
    bl_width_default = 160

    node_options = {
        "default_color": (0.3,0.3,0.3),
        "import_once": True
    }


    def update_operation(self,context):
        self.auto_compile(context)

        if self.operation == "CROSS_PRODUCT":
            self.use_four = False

        if self.operation in ["LENGTH","NORMALIZE"]:
            if len(self.inputs) == 2:
                self.inputs.remove(self.inputs[1])
            else:
                self.add_float_input("b").subtype = "VECTOR3"
        else:
            if len(self.inputs) == 1:
                self.add_float_input("b").subtype = "VECTOR3"

        if self.operation == "DIVIDE":
            self.inputs[1].subtype = "NONE"
        else:
            self.inputs[1].subtype = "VECTOR3"
        
        self.use_four = self.use_four

    def update_four(self,context):
        self.auto_compile(context)

        if self.operation == "CROSS_PRODUCT" and self.use_four:
            self.use_four = False

        for inp in self.inputs:
            if "VECTOR" in inp.subtype:
                if self.use_four:
                    inp.subtype = "VECTOR4"
                else:
                    inp.subtype = "VECTOR3"

    use_four: bpy.props.BoolProperty(name="Vector4",default=False,description="Use Vectors with four values instead of three",update=update_four)

    operation: bpy.props.EnumProperty(items=[("ADD", "Add", "Add two vectors"),
                                             ("SUBTRACT", "Subtract", "Subtract two vectors"),
                                             ("MULTIPLY", "Multiply", "Multiply two vectors"),
                                             ("DIVIDE", "Divide", "Divide two vectors"),
                                             ("CROSS_PRODUCT", "Cross Product", "Cross Product of two vectors"),
                                             ("DOT_PRODUCT", "Dot Product", "Dot Product of two vectors"),
                                             ("LENGTH", "Length", "Length of a vector")],
                                      name="Operation", description="The operation you want to commence",
                                      update=update_operation)
    
    def on_create(self,context):
        self.add_float_input("a").subtype = "VECTOR3"
        self.add_float_input("b").subtype = "VECTOR3"
        self.add_float_output("Result").subtype = "VECTOR3"

    def draw_node(self, context, layout):
        layout.prop(self, "operation", text="")
        if self.operation != "CROSS_PRODUCT":
            layout.prop(self,"use_four")

    def code_imports(self, context):
        return {"code":f"""
                        import mathutils
                        """}

    def code_evaluate(self, context, touched_socket):

        if self.operation == "ADD":
            return {"code": f"tuple(mathutils.Vector({self.inputs[0].code()}) + mathutils.Vector({self.inputs[1].code()}))"}
        elif self.operation == "SUBTRACT":
            return {"code": f"tuple(mathutils.Vector({self.inputs[0].code()}) - mathutils.Vector({self.inputs[1].code()}))"}
        elif self.operation == "MULTIPLY":
            return {"code": f"tuple(mathutils.Vector({self.inputs[0].code()}) * mathutils.Vector({self.inputs[1].code()}))"}
        elif self.operation == "DIVIDE":
            return {"code": f"tuple(mathutils.Vector({self.inputs[0].code()}) / {self.inputs[1].code()})"}
        elif self.operation == "CROSS_PRODUCT":
            return {"code": f"tuple(mathutils.Vector({self.inputs[0].code()}).cross(mathutils.Vector({self.inputs[1].code()})))"}
        elif self.operation == "DOT_PRODUCT":
            return {"code": f"mathutils.Vector({self.inputs[0].code()}).dot(mathutils.Vector({self.inputs[1].code()}))"}
        elif self.operation == "LENGTH":
            return {"code": f"mathutils.Vector({self.inputs[0].code()}).length"}