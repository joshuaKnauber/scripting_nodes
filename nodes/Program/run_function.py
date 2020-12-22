import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_RunFunctionNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_RunFunctionNode"
    bl_label = "Run Function"
    # bl_icon = "GRAPH"
    bl_width_default = 200

    node_options = {
        "default_color": (0.2,0.2,0.2),
        "is_function_node": True
    }

    recursion_warning: bpy.props.BoolProperty()

    def on_outside_update(self, node):
        pass

    def update_name(self, context):
        self.recursion_warning = False
        if self.func_name in self.addon_tree.sn_nodes["SN_FunctionNode"].items:
            item = self.addon_tree.sn_nodes["SN_FunctionNode"].items[self.func_name]
            if self.what_start_idname() == "SN_FunctionNode":
                if self.func_name == self.what_start_node().func_name:
                    self.recursion_warning = True


    func_name: bpy.props.StringProperty(name="Name", description="Name of the function", update=update_name)

    def on_node_update(self):
        self.update_name(None)

    def on_create(self,context):
        self.add_execute_input("Function")
        self.add_execute_output("Execute")


    def draw_node(self,context,layout):
        if self.recursion_warning:
            layout.label(text="Be careful when using recursion!")

        layout.prop_search(self, "func_name", self.addon_tree.sn_nodes["SN_FunctionNode"], "items")


    def code_evaluate(self, context, touched_socket):
        if self.func_name in self.addon_tree.sn_nodes["SN_FunctionNode"].items:
            return {
                "code": f"""
                    {self.addon_tree.sn_nodes["SN_FunctionNode"].items[self.func_name].identifier}()
                    {self.outputs[0].block(5)}
                    """
            }

        else:
            self.add_error("No function", "No valid function selected")
            return {
                "code": {self.outputs[0].block(5)}
            }