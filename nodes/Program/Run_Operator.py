from sqlite3 import paramstyle
import bpy
from ..base_node import SN_ScriptingBaseNode



def on_operator_ref_update(self, node, data, ntree, node_ref_name, input_offset=1):
    if node.node_tree == ntree and node.name == node_ref_name:
        if data:
            if "property_change" in data:
                prop = data["property_change"]
                for inp in self.inputs[input_offset:]:
                    if not inp.name in node.properties:
                        inp.name = prop.name
                    if inp.name == prop.name:
                        if prop.property_type in ["Integer", "Float", "Boolean"] and prop.settings.is_vector:
                            socket = self.convert_socket(inp, self.socket_names[prop.property_type + " Vector"])
                            socket.size = prop.settings.size
                        else:
                            socket = self.convert_socket(inp, self.socket_names[prop.property_type])
                    
                        if hasattr(prop.settings, "subtype"):
                            if prop.settings.subtype in socket.subtypes:
                                socket.subtype = prop.settings.subtype
                            else:
                                socket.subtype = "NONE"

                        if prop.property_type == "Enum":
                            socket.subtype = "CUSTOM_ITEMS"
                            socket.custom_items.clear()
                            for item in prop.settings.items:
                                socket.custom_items.add().name = item.name

        if "property_add" in data:
            prop = data["property_add"]
            self._add_input(self.socket_names[prop.property_type], prop.name).can_be_disabled = True

        if "property_remove" in data:
            self.inputs.remove(self.inputs[data["property_remove"] + input_offset])

        if "property_move" in data:
            from_index = data["property_move"][0]
            to_index = data["property_move"][1]
            self.inputs.move(from_index+input_offset, to_index+input_offset)

        self._evaluate(bpy.context)



class SN_RunOperatorNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_RunOperatorNode"
    bl_label = "Run Operator"
    node_color = "PROGRAM"
    bl_width_default = 200

    def on_create(self, context):
        self.add_execute_input()
        self.add_execute_output()
        
    def get_context_items(self,context):
        items = []
        areas = ["DEFAULT", "VIEW_3D", "IMAGE_EDITOR", "NODE_EDITOR", "SEQUENCE_EDITOR", "CLIP_EDITOR", "DOPESHEET_EDITOR",
                "DOPESHEET_ACTION_EDITOR", "DOPESHEET_SHAPEKEY_EDITOR", "DOPESHEET_GREASE_PENCIL", "DOPESHEET_MASK_EDITOR", "DOPESHEET_CACHE_FILE",
                "GRAPH_EDITOR", "NLA_EDITOR", "TEXT_EDITOR", "CONSOLE", "INFO", "TOPBAR", "STATUSBAR", "OUTLINER",
                "PROPERTIES", "FILE_BROWSER", "PREFERENCES"]
        for area in areas:
            items.append((area,area.replace("_"," ").title(),area.replace("_"," ").title()))
        return items
    
    context: bpy.props.EnumProperty(name="Operator Context", description="The context this operator should run in",
                                    items=get_context_items, update=SN_ScriptingBaseNode._evaluate)
        
    use_invoke: bpy.props.BoolProperty(name="Use Invoke",
                                    description="This will run the before popup output and keep the interactive elements. It won't wait for the operations you connect to this nodes output",
                                    default=True,
                                    update=SN_ScriptingBaseNode._evaluate)

    def on_ref_update(self, node, data=None):
        on_operator_ref_update(self, node, data, self.ref_ntree, self.ref_SN_OperatorNode)

    def reset_inputs(self):
        """ Remove all operator inputs """
        for inp in self.inputs[1:]:
            self.inputs.remove(inp)


    def create_inputs(self, op_rna):
        """ Create inputs for operator """
        for prop in op_rna.properties:
            if not prop.identifier in ["rna_type", "settings"]:
                inp = self.add_input_from_property(prop)
                if inp:
                    inp.can_be_disabled = not prop.is_required
                    inp.disabled = not prop.is_required


    def update_custom_operator(self, context):
        """ Updates the nodes settings when a new parent panel is selected """
        self.reset_inputs()
        if self.ref_ntree and self.ref_SN_OperatorNode in self.ref_ntree.nodes:
            parent = self.ref_ntree.nodes[self.ref_SN_OperatorNode]
            for prop in parent.properties:
                if prop.property_type in ["Integer", "Float", "Boolean"] and prop.settings.is_vector:
                    socket = self._add_input(self.socket_names[prop.property_type + " Vector"], prop.name)
                    socket.size = prop.settings.size
                    socket.can_be_disabled = True
                else:
                    self._add_input(self.socket_names[prop.property_type], prop.name).can_be_disabled = True

        self._evaluate(context)

    def update_source_type(self, context):
        self.hide_disabled_inputs = False
        if self.source_type == "BLENDER":
            self.pasted_operator = self.pasted_operator
        elif self.source_type == "CUSTOM":
            self.ref_SN_OperatorNode = self.ref_SN_OperatorNode
        self._evaluate(context)

    ref_ntree: bpy.props.PointerProperty(type=bpy.types.NodeTree,
                                    name="Panel Node Tree",
                                    description="The node tree to select the operator from",
                                    poll=SN_ScriptingBaseNode.ntree_poll,
                                    update=SN_ScriptingBaseNode._evaluate)

    source_type: bpy.props.EnumProperty(name="Source Type",
                                    description="Use a custom operator or a blender internal",
                                    items=[("BLENDER", "Blender", "Blender", "BLENDER", 0),
                                           ("CUSTOM", "Custom", "Custom", "FILE_SCRIPT", 1)],
                                    update=update_source_type)

    ref_SN_OperatorNode: bpy.props.StringProperty(name="Custom Operator",
                                    description="The operator ran by this button",
                                    update=update_custom_operator)


    def update_pasted_operator(self, context):
        self.reset_inputs()
        
        if self.pasted_operator:
            self.disable_evaluation = True
            op = eval(self.pasted_operator.split("(")[0])
            op_rna = op.get_rna_type()
            self.pasted_name = op_rna.name
            self.create_inputs(op_rna)
            self.disable_evaluation = False
            self._evaluate(context)
    
    pasted_operator: bpy.props.StringProperty(default="bpy.ops.sn.dummy_button_operator()",
                                        update=update_pasted_operator)
    
    pasted_name: bpy.props.StringProperty(default="Paste Operator")
    
    
    def update_hide_disabled_inputs(self, context):
        for inp in self.inputs:
            if inp.can_be_disabled and inp.disabled:
                inp.set_hide(self.hide_disabled_inputs)
    
    hide_disabled_inputs: bpy.props.BoolProperty(default=False,
                                        name="Hide Disabled Inputs",
                                        description="Hides the disabled inputs of this node",
                                        update=update_hide_disabled_inputs)


    def evaluate(self, context):
        context_modes = {
            "DOPESHEET_ACTION_EDITOR": "ACTION",
            "DOPESHEET_SHAPEKEY_EDITOR": "SHAPEKEY",
            "DOPESHEET_GREASE_PENCIL": "GPENCIL",
            "DOPESHEET_MASK_EDITOR": "MASK",
            "DOPESHEET_CACHE_FILE": "CACHEFILE"
        }

        set_context_mode = ""
        set_context = ""
        if self.context != "DEFAULT":
            set_context = f"bpy.context.area.type = '{self.context}'"
            if self.context in context_modes:
                set_context_mode = f"bpy.context.space_data.mode = '{context_modes[self.context]}'"
                set_context = "bpy.context.area.type = 'DOPESHEET_EDITOR'"
        
        invoke = "" if not self.use_invoke else "'INVOKE_DEFAULT', "
        if self.source_type == "BLENDER":
            op_name = self.pasted_operator[8:].split("(")[0]
            op = eval(self.pasted_operator.split("(")[0])
            op_rna = op.get_rna_type()
            parameters = ""
            for inp in self.inputs[1:]:
                if not inp.disabled:
                    for prop in op_rna.properties:
                        if prop.name == inp.name:
                            parameters += f"{prop.identifier}={inp.python_value}, "

            self.code = f"""
                        {'prev_context = bpy.context.area.type' if set_context else ''}
                        {set_context}
                        {set_context_mode}
                        bpy.ops.{op_name}({invoke}{parameters[:-2]})
                        {'bpy.context.area.type = prev_context' if set_context else ''}
                        {self.indent(self.outputs[0].python_value, 6)}
                        """

        else:
            self.code = f"""
                        {self.indent(self.outputs[0].python_value, 6)}
                        """

            if self.ref_ntree and self.ref_SN_OperatorNode:
                node = self.ref_ntree.nodes[self.ref_SN_OperatorNode]
                parameters = ""
                for inp in self.inputs[1:]:
                    if not inp.disabled:
                        for prop in node.properties:
                            if prop.name == inp.name:
                                parameters += f"{prop.python_name}={inp.python_value}, "

                self.code = f"""
                            {'prev_context = bpy.context.area.type' if set_context else ''}
                            {set_context}
                            {set_context_mode}
                            bpy.ops.sna.{node.operator_python_name}({invoke}{parameters[:-2]})
                            {'bpy.context.area.type = prev_context' if set_context else ''}
                            {self.indent(self.outputs[0].python_value, 7)}
                            """


    def draw_node(self, context, layout):
        row = layout.row(align=True)
        row.prop(self, "source_type", text="", icon_only=True)
        
        if self.source_type == "BLENDER":
            op = row.operator("sn.paste_operator", text=self.pasted_name if self.pasted_operator else "Paste Operator", icon="PASTEDOWN")
            op.node_tree = self.node_tree.name
            op.node = self.name

        elif self.source_type == "CUSTOM":
            parent_tree = self.ref_ntree if self.ref_ntree else self.node_tree
            row.prop_search(self, "ref_ntree", bpy.data, "node_groups", text="")
            subrow = row.row(align=True)
            subrow.enabled = self.ref_ntree != None
            subrow.prop_search(self, "ref_SN_OperatorNode", bpy.data.node_groups[parent_tree.name].node_collection("SN_OperatorNode"), "refs", text="")

        row.prop(self, "hide_disabled_inputs", text="", icon="HIDE_ON" if self.hide_disabled_inputs else "HIDE_OFF", emboss=False)
        
        layout.prop(self, "context")
        layout.prop(self, "use_invoke")