import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_MoveCollectionItemNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_MoveCollectionItemNode"
    bl_label = "Move Collection Item"
    node_color = "PROPERTY"
    

    def on_create(self, context):
        self.add_execute_input()
        self.add_collection_property_input(label="Serpens Collection Property")
        self.add_integer_input("Move From")
        self.add_integer_input("Move To")
        self.add_execute_output()
        self.add_property_output("Item")


    def evaluate(self, context):
        if self.inputs[1].is_linked:
            self.code = f"""
                        {self.inputs[1].python_value}.move({self.inputs['Move From'].python_value}, {self.inputs['Move To'].python_value})
                        item_{self.static_uid} = {self.inputs[1].python_value}[{self.inputs['Move To'].python_value}]
                        {self.indent(self.outputs[0].python_value, 6)}
                        """
            self.outputs["Item"].python_value = f"item_{self.static_uid}"
        else:
            self.outputs["Item"].reset_value()