from pickle import TUPLE
import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_IsIndexInCollectionPropertyNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_IsIndexInCollectionPropertyNode"
    bl_label = "Is Index In Collection"
    node_color = "PROPERTY"
    
    def on_create(self, context):
        self.add_collection_property_input()
        self.add_integer_input("Index")
        self.add_boolean_output("In Collection")
        self.add_integer_output("Index")

    def update_index_type(self, context):
        self.convert_socket(self.inputs[1], self.socket_names[self.index_type])
        self._evaluate(context)
        
    index_type: bpy.props.EnumProperty(name="Index Type",
                                description="The type of index to use",
                                items=[("Integer", "Index", "Starts at 0. Negative indices go to the back of the list."),
                                       ("String", "Name", "Refers to the name property of the element.")],
                                update=update_index_type)
        
    def evaluate(self, context):
        self.code_imperative = f"""
            def property_exists(prop_path, glob, loc):
                try:
                    eval(prop_path, glob, loc)
                    return True
                except:
                    return False
            """
            
        if self.inputs[0].is_linked:
            if self.index_type == "Integer":
                self.outputs["In Collection"].python_value = f"""(property_exists("{self.inputs[0].python_value}", globals(), locals()) and len({self.inputs[0].python_value}) > {self.inputs[1].python_value})"""
                self.outputs["Index"].python_value = self.inputs[1].python_value
            else:
                self.outputs["In Collection"].python_value = f"""(property_exists("{self.inputs[0].python_value}", globals(), locals()) and {self.inputs[1].python_value} in {self.inputs[0].python_value})"""
                self.outputs["Index"].python_value = f"{self.inputs[0].python_value}.find({self.inputs[1].python_value})"
        else:
            self.outputs[0].reset_value()
            self.outputs[1].reset_value()

    def draw_node(self, context, layout):
        layout.prop(self, "index_type", expand=True)