import bpy
from ...utils import get_python_name
from ..base_node import SN_ScriptingBaseNode



class SN_RunInterfaceFunctionNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_RunInterfaceFunctionNode"
    bl_label = "Function Run (Interface)"
    bl_width_default = 200

    def on_create(self, context):
        self.add_interface_input()


    def on_ref_update(self, node, data=None):
        if node.bl_idname == "SN_InterfaceFunctionNode" and data:
            index = 0
            for i, out in enumerate(node.outputs):
                if out.bl_idname != "SN_InterfaceSocket":
                    index = i-1
                    break
            # inputs has been added
            if "added" in data:
                self.add_input_from_socket(data["added"])
            # input has been removed
            elif "removed" in data:
                self.inputs.remove(self.inputs[data["removed"]])
            # input has changed
            elif "changed" in data:
                self.convert_socket(self.inputs[data["changed"].index-index], data["changed"].bl_idname)
            # input has updated
            elif "updated" in data:
                if data["updated"].index-index < len(self.inputs):
                    self.inputs[data["updated"].index-index].name = data["updated"].name
            self._evaluate(bpy.context)


    def update_function_reference(self, context):
        parent_tree = self.custom_parent_ntree if self.custom_parent_ntree else self.node_tree
        # remember connections
        links = []
        for inp in self.inputs[1:]:
            links.append(None)
            if inp.is_linked:
                links[-1] = inp.from_socket()
        # remove current data inputs
        for i in range(len(self.inputs)-1, 0, -1):
            self.inputs.remove(self.inputs[i])
        # add new data inputs
        if self.ref_SN_InterfaceFunctionNode in parent_tree.nodes:
            for out in parent_tree.nodes[self.ref_SN_InterfaceFunctionNode].outputs[1:-1]:
                if out.bl_idname != "SN_InterfaceSocket":
                    self.add_input_from_socket(out)
        # restore connections
        if len(links) == len(self.inputs)-1:
            for i, from_socket in enumerate(links):
                if from_socket:
                    self.node_tree.links.new(from_socket, self.inputs[i+1])
        self._evaluate(context)

    ref_SN_InterfaceFunctionNode: bpy.props.StringProperty(name="Function",
                                            description="The function to run",
                                            update=update_function_reference)

    custom_parent_ntree: bpy.props.PointerProperty(type=bpy.types.NodeTree,
                                    name="Panel Node Tree",
                                    description="The node tree to select the panel from",
                                    poll=SN_ScriptingBaseNode.ntree_poll,
                                    update=SN_ScriptingBaseNode._evaluate)


    def evaluate(self, context):
        parent_tree = self.custom_parent_ntree if self.custom_parent_ntree else self.node_tree
        if self.ref_SN_InterfaceFunctionNode in parent_tree.nodes:
            # get input values
            inp_values = []
            for inp in self.inputs[1:]:
                inp_values.append(inp.python_value)
            inp_values = ", ".join(inp_values)

            self.code = f"""
                        layout_function = {self.active_layout}
                        {parent_tree.nodes[self.ref_SN_InterfaceFunctionNode].func_name}(layout_function, {inp_values})
                        """
        else:
            self.code = f""


    def draw_node(self, context, layout):
        row = layout.row(align=True)
        parent_tree = self.custom_parent_ntree if self.custom_parent_ntree else self.node_tree
        row.prop_search(self, "custom_parent_ntree", bpy.data, "node_groups", text="")
        subrow = row.row(align=True)
        subrow.enabled = self.custom_parent_ntree != None
        subrow.prop_search(self, "ref_SN_InterfaceFunctionNode", bpy.data.node_groups[parent_tree.name].node_collection("SN_InterfaceFunctionNode"), "refs", text="")
