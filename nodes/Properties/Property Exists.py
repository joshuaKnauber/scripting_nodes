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
        self.code_imperative = f"""
            def property_exists(prop_path):
                try:
                    eval(prop_path)
                    return True
                except:
                    return False
            """
        self.outputs[0].python_value = f"""property_exists("{self.inputs[0].python_value}")"""
