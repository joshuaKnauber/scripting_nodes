import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_ReturnNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_ReturnNode"
    bl_label = "Return"
    # bl_icon = "GRAPH"
    bl_width_default = 180

    node_options = {
        "default_color": (0.3,0.3,0.3),
    }

    connected_function: bpy.props.BoolProperty(default=True)

    def on_create(self,context):
        self.add_execute_input("Return")
        self.add_dynamic_data_input("Content")


    def on_node_update(self):
        if len(self.inputs[0].links):
            if self.what_start_idname() == "SN_FunctionNode":
                self.connected_function = True
            else:
                self.connected_function = False
        else:
            self.connected_function = True
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
                        return {self.list_blocks(contents, 0)}
                        """
            }
        else:
            self.add_error("No function", "This node has to be connected to a function", False)
            return {"code": {self.list_blocks(contents, 0)}}