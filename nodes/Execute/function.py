import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_FunctionNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_FunctionNode"
    bl_label = "Function"
    # bl_icon = "GRAPH"
    bl_width_default = 160

    node_options = {
        "default_color": (0.3,0.3,0.3),
        "starts_tree": True
    }

    def update_name(self, context):
        unique_name = self.func_name
        if not unique_name:
            unique_name = "New Function"

        unique_name = self.get_unique_name(unique_name, context.scene.sn_function_nodes, " ")
        if unique_name != self.func_name:
            self.func_name = unique_name


    func_name: bpy.props.StringProperty(name="Name", description="Name of the function", update=update_name)


    def on_create(self,context):
        self.add_execute_output("Execute")
        self.add_dynamic_data_output("Parameter")


    def draw_node(self,context,layout):
        layout.prop(self, "func_name")


    def on_link_insert(self,link):
        if link.from_socket.name == "Parameter" and link.from_socket.removable:
            for index, out in enumerate(self.outputs):
                if out == link.from_socket:
                    self.outputs[index].name = link.to_socket.name


    def code_imperative(self, context, main_tree):

        return {
            "code": f"""

                    row = {layout}.row(align={self.inputs["Align"].value})
                    row.enabled = {self.inputs["Enabled"].value}
                    row.alert = {self.inputs["Alert"].value}
                    row.scale_x = {self.inputs["Scale X"].value}
                    row.scale_y = {self.inputs["Scale Y"].value}
                    {self.list_blocks(row_layouts, 5)}

                    """
        }