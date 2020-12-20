import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_FunctionNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_FunctionNode"
    bl_label = "Function"
    # bl_icon = "GRAPH"
    bl_width_default = 160

    node_options = {
        "default_color": (0.3,0.3,0.3),
        "starts_tree": True,
        "has_collection": True
    }

    def update_name(self, context):
        if not self.func_name:
            self.func_name = "New Function"
            
        self.item.name = self.func_name
        self.item.identifier = self.get_python_name(self.func_name, "new_function")

        unique_name = self.get_unique_name(self.func_name, self.collection.items, " ")
        if unique_name != self.func_name:
            self.func_name = unique_name
        
        self.item.name = self.func_name
        self.item.identifier = self.get_python_name(self.func_name, "new_function")


    func_name: bpy.props.StringProperty(name="Name", description="Name of the function", update=update_name)


    def on_create(self,context):
        self.add_execute_output("Execute")
        self.add_dynamic_data_output("Parameter").take_name = True
        self.update_name(None)


    def draw_node(self,context,layout):
        layout.prop(self, "func_name")


    def code_imperative(self, context):
        parameter = []
        for out in self.outputs[1:-1]:
            parameter.append(self.get_python_name(out.get_text(""), "parameter") + ", ")

        parameter_string = ""
        for item in parameter:
            parameter_string+=item
        parameter_string = parameter_string[:-2]

        return {
            "code": f"""
                    def {self.item.identifier}({parameter_string}):
                        {self.outputs[0].block(6)}
                        
                    """
        }