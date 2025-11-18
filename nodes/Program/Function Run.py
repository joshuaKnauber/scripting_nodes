import bpy
from ...utils import get_python_name
from ..base_node import SN_ScriptingBaseNode



class SN_RunFunctionNode(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_RunFunctionNode"
    bl_label = "Function Run (Execute)"
    bl_width_default = 240

    def on_create(self, context):
        self.add_execute_input()
        self.add_execute_output()
        self.ref_ntree = self.node_tree


    def update_enum_socket(self, from_socket, to_socket):
        to_socket.subtype = "CUSTOM_ITEMS"
        to_socket.custom_items_editable = False
        to_socket.custom_items.clear()
        for item in from_socket.custom_items:
            new = to_socket.custom_items.add()
            new.name = item.name
            
    def update_vector_socket(self, from_socket, to_socket):
        to_socket.size = from_socket.size
        
            
    def on_ref_update(self, node, data=None):
        if node.bl_idname == "SN_FunctionNode" and data:
            # inputs has been added
            if "added" in data:
                socket_index = list(data["added"].node.outputs).index(data["added"])
                new_socket = self.add_input_from_socket(data["added"])
                # Ensure the socket name is set correctly
                if new_socket and data["added"].name:
                    new_socket.set_name_silent(data["added"].name)
                self.inputs.move(len(self.inputs)-1, socket_index)
            # input has been removed
            elif "removed" in data:
                self.inputs.remove(self.inputs[data["removed"]])
            # input has changed
            elif "changed" in data:
                self.convert_socket(self.inputs[data["changed"].index], data["changed"].bl_idname)
                # update enum items
                if data["changed"].bl_label == "Enum" or data["changed"].bl_label == "Enum Set":
                    self.update_enum_socket(data["changed"], self.inputs[data["changed"].index])
                elif "Vector" in data["changed"].bl_label:
                    self.update_vector_socket(data["changed"], self.inputs[data["changed"].index])
            # input has updated
            elif "updated" in data:
                # Use new_name from data if available, otherwise fall back to socket.name
                socket_name = data.get("new_name", data["updated"].name)
                self.inputs[data["updated"].index].set_name_silent(socket_name)
            self._evaluate(bpy.context)
        elif node.bl_idname == "SN_FunctionReturnNode" and data:
            # output has been added
            if "added" in data:
                socket_index = list(data["added"].node.inputs).index(data["added"])
                new_socket = self.add_output_from_socket(data["added"])
                # Ensure the socket name is set correctly
                if new_socket and data["added"].name:
                    new_socket.set_name_silent(data["added"].name)
                self.outputs.move(len(self.outputs)-1, socket_index)
            # output has been removed
            elif "removed" in data:
                self.outputs.remove(self.outputs[data["removed"]])
            # output has changed
            elif "changed" in data:
                self.convert_socket(self.outputs[data["changed"].index], data["changed"].bl_idname)
            # output has updated
            elif "updated" in data:
                # Use new_name from data if available, otherwise fall back to socket.name
                socket_name = data.get("new_name", data["updated"].name)
                self.outputs[data["updated"].index].set_name_silent(socket_name)
            self._evaluate(bpy.context)


    def update_function_reference(self, context):
        parent_tree = self.ref_ntree if self.ref_ntree else self.node_tree
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
        if self.ref_SN_FunctionNode in parent_tree.nodes:
            for out in parent_tree.nodes[self.ref_SN_FunctionNode].outputs[1:-1]:
                inp = self.add_input_from_socket(out)
                # Ensure the socket name is set correctly
                if inp and out.name:
                    inp.set_name_silent(out.name)
                # update enum items
                if out.bl_label == "Enum" or out.bl_label == "Enum Set":
                    self.update_enum_socket(out, inp)
                elif "Vector" in out.bl_label:
                    self.update_vector_socket(out, inp)
        # restore connections
        if len(links) == len(self.inputs)-1:
            for i, from_socket in enumerate(links):
                if from_socket:
                    self.node_tree.links.new(from_socket, self.inputs[i+1])
        self._evaluate(context)
    
    def update_function_return_reference(self, context):
        parent_tree = self.ref_ntree if self.ref_ntree else self.node_tree
        # remember connections
        links = []
        for out in self.outputs[1:]:
            links.append([])
            if out.is_linked:
                links[-1] = out.to_sockets()
        # remove current data outputs
        for i in range(len(self.outputs)-1, 0, -1):
            self.outputs.remove(self.outputs[i])
        # add new data outputs
        if self.ref_SN_FunctionReturnNode in parent_tree.nodes:
            for out in parent_tree.nodes[self.ref_SN_FunctionReturnNode].inputs[1:-1]:
                new_socket = self.add_output_from_socket(out)
                # Ensure the socket name is set correctly
                if new_socket and out.name:
                    new_socket.set_name_silent(out.name)
        # restore connections
        if len(links) == len(self.outputs)-1:
            for i, to_sockets in enumerate(links):
                for to_socket in to_sockets:
                    self.node_tree.links.new(self.outputs[i+1], to_socket)
        self._evaluate(context)
    
    ref_SN_FunctionNode: bpy.props.StringProperty(name="Function",
                                            description="The function to run",
                                            update=update_function_reference)

    ref_SN_FunctionReturnNode: bpy.props.StringProperty(name="Return",
                                            description="The return node to get values from",
                                            update=update_function_return_reference)
    
    ref_ntree: bpy.props.PointerProperty(type=bpy.types.NodeTree,
                                    name="Panel Node Tree",
                                    description="The node tree to select the panel from",
                                    poll=SN_ScriptingBaseNode.ntree_poll,
                                    update=SN_ScriptingBaseNode._evaluate)
    
    
    def update_require_execute(self, context):
        self.inputs[0].set_hide(not self.require_execute)
        self.outputs[0].set_hide(not self.require_execute)
        self._evaluate(context)

    require_execute: bpy.props.BoolProperty(name="Require Execute", default=True,
                                        description="Removes the execute inputs and only gives you the return value",
                                        update=update_require_execute)


    def evaluate(self, context):
        parent_tree = self.ref_ntree if self.ref_ntree else self.node_tree
        if self.ref_SN_FunctionNode in parent_tree.nodes:
            # get input values
            inp_values = []
            for inp in self.inputs[1:]:
                inp_values.append(inp.python_value)
            inp_values = ", ".join(inp_values)

            if self.require_execute:
                # get return variable names
                return_values = []
                for i, out in enumerate(self.outputs[1:]):
                    return_values.append(get_python_name(f"{out.name}_{i}_{self.static_uid}", f"parameter_{i}_{self.static_uid}"))
                return_names = ", ".join(return_values)

                # set values with execute
                if return_names:
                    self.code = f"{return_names} = {parent_tree.nodes[self.ref_SN_FunctionNode].func_name}({inp_values})"
                else:
                    self.code = f"{parent_tree.nodes[self.ref_SN_FunctionNode].func_name}({inp_values})"
                for i, out in enumerate(self.outputs[1:]):
                    out.python_value = return_values[i]
            else:
                # set values without execute
                if len(self.outputs) > 2:
                    for i, out in enumerate(self.outputs[1:]):
                        out.python_value = f"{parent_tree.nodes[self.ref_SN_FunctionNode].func_name}({inp_values})[{i}]"
                elif len(self.outputs) == 2:
                    self.outputs[-1].python_value = f"{parent_tree.nodes[self.ref_SN_FunctionNode].func_name}({inp_values})"
        else:
            for out in self.outputs[1:]:
                out.reset_value()
        
        if self.require_execute:
            self.code += f"\n{self.outputs[0].python_value}"

    
    def draw_node(self, context, layout):
        row = layout.row(align=True)
        parent_tree = self.ref_ntree if self.ref_ntree else self.node_tree
        row.prop_search(self, "ref_ntree", bpy.data, "node_groups", text="")
        subrow = row.row(align=True)
        subrow.enabled = self.ref_ntree != None
        subrow.prop_search(self, "ref_SN_FunctionNode", bpy.data.node_groups[parent_tree.name].node_collection("SN_FunctionNode"), "refs", text="")

        subrow = row.row()
        subrow.enabled = self.ref_ntree != None and self.ref_SN_FunctionNode in self.ref_ntree.nodes
        op = subrow.operator("sn.find_node", text="", icon="RESTRICT_SELECT_OFF", emboss=False)
        op.node_tree = self.ref_ntree.name if self.ref_ntree else ""
        op.node = self.ref_SN_FunctionNode

        row = layout.row()
        row.enabled = self.ref_ntree != None
        row.prop_search(self, "ref_SN_FunctionReturnNode", bpy.data.node_groups[parent_tree.name].node_collection("SN_FunctionReturnNode"), "refs", text="Return")

        subrow = row.row()
        subrow.enabled = self.ref_ntree != None and self.ref_SN_FunctionReturnNode in self.ref_ntree.nodes
        op = subrow.operator("sn.find_node", text="", icon="RESTRICT_SELECT_OFF", emboss=False)
        op.node_tree = self.ref_ntree.name if self.ref_ntree else ""
        op.node = self.ref_SN_FunctionReturnNode

        layout.prop(self, "require_execute")
        
        if self.ref_ntree and self.ref_SN_FunctionNode and self.ref_SN_FunctionReturnNode:
            return_node = self.ref_ntree.nodes[self.ref_SN_FunctionReturnNode]
            if not self.ref_ntree.nodes[self.ref_SN_FunctionNode] in return_node.root_nodes:
                row = layout.row()
                row.alert = True
                row.label(text="Return node not connected to function node!", icon="ERROR")