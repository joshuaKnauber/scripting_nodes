import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_PropertyExistsNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_PropertyExistsNode"
    bl_label = "Property Exists"
    node_color = "PROPERTY"


    def on_create(self, context):
        self.add_property_input()
        self.add_boolean_output("Property Exists")


    def evaluate(self, context):
        sections = self.inputs[0].python_sections
        parts = []
        path = ""
        for section in sections:
            if section[0] == "[" and section[-1] == "]":
                if section[1:-1].isdigit():
                    parts.append(f"len({path}) > {section[1:-1]}")
                else:
                    parts.append(f"{section[1:-1]} in {path}")
                path += section
            else:
                if path:
                    parts.append(f"""hasattr({path}, "{section}")""")
                    path += "." + section
                else:
                    path += section
        if parts:
            self.outputs[0].python_value = f"({' and '.join(parts)})"
        else:
            self.outputs[0].python_value = f"False"