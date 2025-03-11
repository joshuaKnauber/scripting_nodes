from scripting_nodes.src.lib.utils.code.format import indent
from scripting_nodes.src.features.nodes.base_node import ScriptingBaseNode
import bpy


class SNA_Node_String_Adjust_func(ScriptingBaseNode, bpy.types.Node):
    bl_idname = "SNA_Node_String_Adjust_func"
    bl_label = "String Adjust Function"

    def update_value(self, context):
        self._generate()

    value_new: bpy.props.EnumProperty(
        name="Test",
        description="Select a string transformation mode",
        items=[
            ("LOWER", "Lowercase", "Convert to lowercase"),
            ("UPPER", "Uppercase", "Convert to uppercase"),
            ("CAMEL", "Camel Case", "Convert to camel case"),
        ],
        default="LOWER",
        update=update_value,
    )

    def draw(self, context, layout):
        layout.prop(self, "value_new", text="Options", placeholder="Value")
        
    def on_create(self):
        self.add_input("ScriptingProgramSocket")
        self.add_input("ScriptingStringSocket", "Value")
        self.add_output("ScriptingProgramSocket")
        self.add_output("ScriptingStringSocket", "Value")


    def generate(self):
        self.code = f"""
            def tester(input_str):
            
                if "{self.value_new}" == "LOWER":
                    return input_str.lower()
                elif "{self.value_new}" == "UPPER":
                    return input_str.upper()
                elif "{self.value_new}" == "CAMEL":
                    return ' '.join(word.capitalize() for word in input_str.split())
                else:
                    return input_str  # Default: return as is

            var_{self.id} = tester({self.inputs[1].eval()})

            {indent(self.outputs[0].eval(), 3)}
        """
        self.outputs[1].code = f"var_{self.id}"
