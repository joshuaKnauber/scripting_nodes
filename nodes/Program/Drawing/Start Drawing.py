import bpy
from ...base_node import SN_ScriptingBaseNode



class SN_StartDrawingNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_StartDrawingNode"
    bl_label = "Start Drawing"
    node_color = "PROGRAM"
    bl_width_default = 200    

    draw_type: bpy.props.EnumProperty(
        name="Draw Type",
        description="The type of drawing that should be started",
        items=[("POST_PIXEL", "2D", "Post Pixel"), ("POST_VIEW", "3D", "Post View"), ("BACKDROP", "Backdrop", "Backdrop for node editors")],
        default="POST_PIXEL",
        update=SN_ScriptingBaseNode._evaluate)


    def update_enum_socket(self, from_socket, to_socket):
        to_socket.subtype = "CUSTOM_ITEMS"
        to_socket.custom_items_editable = False
        to_socket.custom_items.clear()
        for item in from_socket.custom_items:
            new = to_socket.custom_items.add()
            new.name = item.name
            
    def update_vector_socket(self, from_socket, to_socket):
        to_socket.size = from_socket.size
        to_socket.subtype = from_socket.subtype


    def on_ref_update(self, node, data=None):
        if node.bl_idname == "SN_FunctionNode" and data:
            # inputs has been added
            if "added" in data:
                socket_index = list(data["added"].node.outputs).index(data["added"])
                self.add_input_from_socket(data["added"])
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
                self.inputs[data["updated"].index].name = data["updated"].name
            self._evaluate(bpy.context)
        elif node.bl_idname == "SN_FunctionReturnNode" and data:
            # output has been added
            if "added" in data:
                socket_index = list(data["added"].node.inputs).index(data["added"])
                self.add_output_from_socket(data["added"])
                self.outputs.move(len(self.outputs)-1, socket_index)
            # output has been removed
            elif "removed" in data:
                self.outputs.remove(self.outputs[data["removed"]])
            # output has changed
            elif "changed" in data:
                self.convert_socket(self.outputs[data["changed"].index], data["changed"].bl_idname)
            # output has updated
            elif "updated" in data:
                self.outputs[data["updated"].index].name = data["updated"].name
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

    def update_references(self, context):
        self.update_function_reference(context)
        self.trigger_ref_update(self)
        self._evaluate(context)

    ref_SN_FunctionNode: bpy.props.StringProperty(name="Function",
                                            description="The function to run",
                                            update=update_references)

    ref_ntree: bpy.props.PointerProperty(type=bpy.types.NodeTree,
                                    name="Function Node Tree",
                                    description="The node tree to select the function from",
                                    poll=SN_ScriptingBaseNode.ntree_poll,
                                    update=SN_ScriptingBaseNode._evaluate)

    def draw_space_items(self, context):
        items = []
        names = ["SpaceView3D", "SpaceNodeEditor", "SpaceClipEditor", "SpaceConsole", "SpaceDopeSheetEditor", "SpaceFileBrowser",
                "SpaceGraphEditor", "SpaceImageEditor", "SpaceInfo", "SpaceNLA", "SpaceOutliner", "SpacePreferences",
                "SpaceProperties", "SpaceSequenceEditor", "SpaceSpreadsheet", "SpaceTextEditor"]
        for name in names:
            items.append((name, name, name))
        return items
    
    draw_space: bpy.props.EnumProperty(name="Draw Space",
                            description="The space this operator can run in and the text is drawn in",
                            update=update_references,
                            items=draw_space_items)

    def on_create(self, context):
        self.add_execute_input()
        self.add_execute_output()
        self.ref_ntree = self.node_tree

    def draw_node(self, context, layout):
        layout.prop(self, "name")

        row = layout.row(align=True)
        parent_tree = self.ref_ntree if self.ref_ntree else self.node_tree
        row.prop_search(self, "ref_ntree", bpy.data, "node_groups", text="")
        subrow = row.row(align=True)
        subrow.enabled = self.ref_ntree != None
        subrow.prop_search(self, "ref_SN_FunctionNode", bpy.data.node_groups[parent_tree.name].node_collection("SN_FunctionNode"), "refs", text="")

        layout.prop(self, "draw_type")
        layout.prop(self, "draw_space", text="Space")
        
    def evaluate(self, context):
        func = None
        if self.ref_ntree and self.ref_SN_FunctionNode in self.ref_ntree.nodes:
            func = self.ref_ntree.nodes[self.ref_SN_FunctionNode]

            # get input values
            inp_values = []
            for inp in self.inputs[1:]:
                inp_values.append(inp.python_value)
            inp_values = ", ".join(inp_values)
            if inp_values:
                inp_values += ", "

            self.code_imperative = f"""
                handler_{self.static_uid} = []
            """

            self.code = f"""
                handler_{self.static_uid}.append(bpy.types.{self.draw_space}.draw_handler_add({func.func_name}, ({inp_values}), 'WINDOW', '{self.draw_type}'))
                {self.indent(self.outputs[0].python_value, 4)}
            """

            self.code_unregister = f"""
                if handler_{self.static_uid}:
                    bpy.types.{self.draw_space}.draw_handler_remove(handler_{self.static_uid}[0], 'WINDOW')
                    handler_{self.static_uid}.pop(0)
            """