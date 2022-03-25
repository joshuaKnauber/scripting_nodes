import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_RunPropertyFunctionNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_RunPropertyFunctionNode"
    bl_label = "Run Property Function"
    node_color = "PROPERTY"
    
    
    def _disect_data_path(self, path):
        # remove assign part
        path = "(".join(path.split("(")[:-1])
        path = path.strip()
        # replace escaped quotes
        path = path.replace('\\"', '"')
        # split data path in segments
        segments = []
        for segment in path.split(".")[1:]:
            if segments and "[" in segments[-1] and not "]" in segments[-1]:
                segments[-1] += f".{segment}"
            else:
                segments.append(segment)
        # remove indexing from property name
        # segments[-1] = segments[-1].split("[")[0]
        return segments
    
    def _is_valid_data_path(self, path):
        return path and "bpy." in path and not ".ops." in path

    def get_data(self):
        if self._is_valid_data_path(self.pasted_data_path):
            return self._disect_data_path(self.pasted_data_path)
        return None
    
    
    def segment_is_indexable(self, segment):
        """ Returns if a segment can be indexed. A segment is a string part of a data path """
        return "[" in segment and "]" in segment
    
    def add_socket_from_param(self, param, callback):
        """ Adds a socket from the given parameter with the given add callback """
        socket_type = param.split(": ")[1].split("[")[0]
        socket_name = param.split(": ")[0].replace("_", " ").title()
        socket = callback(self.socket_names[socket_type], socket_name)
        socket.can_be_disabled = True
        socket.disabled = True
        if socket_type == "Enum":
            socket.items = f"[{param.split(': ')[1].split('[')[1]}"
    
    def create_inputs_from_path(self):
        """ Creates the inputs for the given data path """
        # remove existing inputs
        for _ in range(len(self.inputs)-1):
            self.inputs.remove(self.inputs[1])
        # create blend data path inputs
        data = self.get_data()
        if data:
            for segment in data:
                if self.segment_is_indexable(segment):
                    name = segment.split("[")[0].replace("_", " ").title()
                    if '"' in segment or "'" in segment:
                        inp = self.add_string_input(name)
                        inp["default_value"] = segment.split("[")[-1].split("]")[0][1:-1]
                        inp.index_type = "String"
                    else:
                        inp = self.add_integer_input(name)
                        inp["default_value"] = int(segment.split("[")[-1].split("]")[0])
                        inp.index_type = "Integer"
                    inp.indexable = True
        # create parameter inputs
        params = self.pasted_data_path.split("(")[-1].split(")")[0].split(", ")
        for param in params:
            self.add_socket_from_param(param, self._add_input)
                    
    def create_outputs_from_path(self):
        # remove existing outputs
        for _ in range(len(self.outputs)-1):
            self.outputs.remove(self.outputs[1])
        # add new outputs
        if " = " in self.pasted_data_path:
            params = self.pasted_data_path.split(" = ")[-1].split(", ")
            for param in params:
                self.add_socket_from_param(param, self._add_output)
        
        
    def get_pasted_prop_name(self):
        if self.pasted_data_path:
            return self.pasted_data_path.split(".")[-1].split("(")[0].replace("_", " ").title()
        return "Property Function"
    
    def on_prop_change(self, context):
        self.label = self.get_pasted_prop_name()
        self.create_inputs_from_path()
        self.create_outputs_from_path()
        self._evaluate(context)
        
    pasted_data_path: bpy.props.StringProperty(name="Pasted Path",
                                description="The full data path to the property",
                                update=on_prop_change)
    

    def on_create(self, context):
        self.add_execute_input()
        self.add_execute_output()
        
        
    def update_require_execute(self, context):
        self.inputs[0].set_hide(not self.require_execute)
        self.outputs[0].set_hide(not self.require_execute)
        self._evaluate(context)
        
    require_execute: bpy.props.BoolProperty(name="Require Execute", default=True,
                                        description="Removes the execute inputs and only gives you the return value",
                                        update=update_require_execute)


    def evaluate(self, context):
        if self.pasted_data_path:
            function_name = "(".join(self.pasted_data_path.split("(")[:-1]).split(".")[-1] + "("

            data_path = ""
            function = data_path + function_name

            # add function parameters
            inp_params = self.pasted_data_path.split("(")[-1].split(")")[0].split(", ")
            for i, param in enumerate(inp_params):
                param_inp = self.inputs[len(self.inputs) - len(inp_params)+i]
                if not param_inp.disabled:
                    function += f"{param.split(': ')[0]}={param_inp.python_value}, "
            function += ")"
            
            # add output parameters
            out_params = self.pasted_data_path.split(" = ")[-1].split(", ")
            if self.require_execute:
                results = ""
                if " = " in self.pasted_data_path:
                    for i, param in enumerate(out_params):
                        name = param.split(": ")[0]
                        results += f"{name}, "
                        self.outputs[i+1].python_value = name
                if results: results = results[:-2] + " = "
                # code
                self.code = f"""
                            {results}{function}
                            {self.indent(self.outputs[0].python_value, 7)}
                            """           
            # no execute
            else:
                if len(self.outputs) == 2:
                    self.outputs[1].python_value = function
                elif len(self.outputs) > 2:
                    for i, out in enumerate(self.outputs):
                        if not i == 0:
                            out.python_value = f"{function}[{i-1}]"
        

    def draw_node(self, context, layout):
        row = layout.row(align=True)
        row.scale_y = 1.2
        op = row.operator("sn.paste_data_path", text=self.get_pasted_prop_name() if self.pasted_data_path else "Paste Function", icon="PASTEDOWN")
        op.node = self.name
        op.node_tree = self.node_tree.name
        if self.pasted_data_path:
            op = row.operator("sn.reset_data_path", text="", icon="LOOP_BACK")
            op.node = self.name
            op.node_tree = self.node_tree.name
            
            if len(self.outputs) > 1:
                layout.prop(self, "require_execute")
            
    def draw_node_panel(self, context, layout):
        layout.prop(self, "pasted_data_path", text="Function Path")