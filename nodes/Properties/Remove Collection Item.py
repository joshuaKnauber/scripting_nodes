import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_RemoveCollectionItemNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_RemoveCollectionItemNode"
    bl_label = "Remove Collection Item"
    node_color = "PROPERTY"
    

    def on_create(self, context):
        self.add_execute_input()
        self.add_collection_property_input(label="Serpens Collection Property")
        self.add_integer_input("Index")
        self.add_execute_output()


    def update_type(self, context):
        if self.remove_type == "Index":
            inp = self.convert_socket(self.inputs[2], self.socket_names["Integer"])
            inp.name = "Index"
        elif self.remove_type == "Item":
            inp = self.convert_socket(self.inputs[2], self.socket_names["Property"])
            inp.name = "Item"
        self.inputs[2].set_hide(self.remove_type == "All")
        self._evaluate(context)

    remove_type: bpy.props.EnumProperty(name="Type",
                                description="Remove by this type",
                                items=[("Index", "Index", "Index"),
                                       ("Item", "Item", "Item"),
                                       ("All", "All", "All")],
                                update=update_type)


    def evaluate(self, context):
        if self.inputs[1].is_linked:
            if self.remove_type == "Index":
                self.code = f"""
                            if len({self.inputs[1].python_value}) > {self.inputs[2].python_value}:
                                {self.inputs[1].python_value}.remove({self.inputs[2].python_value})
                            {self.indent(self.outputs[0].python_value, 7)}
                            """
            elif self.remove_type == "Item":
                self.code = f"""
                            for i_{self.static_uid} in range(len({self.inputs[1].python_value})):
                                if {self.inputs[1].python_value}[i_{self.static_uid}] == {self.inputs[2].python_value}:
                                    {self.inputs[1].python_value}.remove(i_{self.static_uid})
                                    break
                            {self.indent(self.outputs[0].python_value, 7)}
                            """
            elif self.remove_type == "All":
                self.code = f"""
                            {self.inputs[1].python_value}.clear()
                            {self.indent(self.outputs[0].python_value, 7)}
                            """
            
            
    def draw_node(self, context, layout):
        layout.prop(self, "remove_type", expand=True)