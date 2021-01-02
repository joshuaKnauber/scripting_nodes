import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_ReturnNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_ReturnNode"
    bl_label = "Function Return"
    # bl_icon = "GRAPH"
    bl_width_default = 180

    node_options = {
        "default_color": (0.3,0.3,0.3),
        "has_collection": True
    }

    connected_function: bpy.props.StringProperty()

    def on_outside_update(self, node):
        self.on_any_change()


    def on_create(self,context):
        self.add_execute_input("Return")
        self.add_dynamic_variable_input("Content").use_var_name = False


    def on_any_change(self):
        if len(self.inputs):
            if len(self.inputs[0].links):
                if self.what_start_idname() == "SN_FunctionNode":
                    self.connected_function = self.what_start_node().func_name
                    self.label = self.connected_function
                else:
                    self.connected_function = ""
                    self.label = "Function Return"
            else:
                self.connected_function = "None"
                self.label = "Function Return"
        self.update_nodes_by_type("SN_RunFunctionNode")


    def draw_node(self, context, layout):
        if not self.connected_function:
            layout.label(text="Please connect to a function")


    def code_evaluate(self, context, touched_socket):
        contents = []
        for inp in self.inputs[1:-1]:
            contents.append(inp.value + ", ")

        if not contents:
            self.add_error("No return", "Nothing will be returned from this function", False)
            return {
                "code": ""
            }

        if len(self.inputs[0].links) and self.connected_function:
            return {
                "code": f"""
                        return {self.list_values(contents, 0)}
                        """
            }

        else:
            self.add_error("No function", "This node has to be connected to a function", False)
            return {"code": f"{self.list_values(contents, 0)}"}