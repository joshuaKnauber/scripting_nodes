import bpy
from ..Program.Run_Operator import on_operator_ref_update
from ..base_node import SN_ScriptingBaseNode


class SN_ButtonNodeNew(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_ButtonNodeNew"
    bl_label = "Button"
    node_color = "INTERFACE"
    bl_width_default = 240

    def on_create(self, context):
        self.version = 1
        self.add_interface_input()
        self.add_string_input("Label").default_value = "My Button"
        self.add_boolean_input("Emboss").default_value = True
        self.add_boolean_input("Depress")
        self.add_icon_input("Icon")
        self.add_interface_output().passthrough_layout_type = True
        self.ref_ntree = self.node_tree

    def on_ref_update(self, node, data=None):
        on_operator_ref_update(
            self, node, data, self.ref_ntree, self.ref_SN_OperatorNode, 5
        )

    def reset_inputs(self):
        """Remove all operator inputs"""
        for i in range(len(self.inputs) - 1, -1, -1):
            inp = self.inputs[i]
            if inp.can_be_disabled:
                self.inputs.remove(inp)

    def create_inputs(self, op_rna):
        """Create inputs for operator"""
        for prop in op_rna.properties:
            if not prop.identifier in ["rna_type", "settings"]:
                inp = self.add_input_from_property(prop)
                if inp:
                    inp.can_be_disabled = True
                    inp.disabled = not prop.is_required

    def update_custom_operator(self, context):
        """Updates the nodes settings when a new parent panel is selected"""
        self.reset_inputs()
        if self.ref_ntree and self.ref_SN_OperatorNode in self.ref_ntree.nodes:
            parent = self.ref_ntree.nodes[self.ref_SN_OperatorNode]
            for prop in parent.properties:
                if (
                    prop.property_type in ["Integer", "Float", "Boolean"]
                    and prop.settings.is_vector
                ):
                    socket = self._add_input(
                        self.socket_names[prop.property_type + " Vector"], prop.name
                    )
                    socket.size = prop.settings.size
                    socket.can_be_disabled = True
                elif prop.property_type == "Enum":
                    if prop.stngs_enum.enum_flag:
                        socket = self._add_input(
                            self.socket_names["Enum Set"], prop.name
                        )
                    else:
                        socket = self._add_input(
                            self.socket_names[prop.property_type], prop.name
                        )
                    socket.items = str(
                        list(map(lambda item: item.name, prop.stngs_enum.items))
                    )
                else:
                    self._add_input(
                        self.socket_names[prop.property_type], prop.name
                    ).can_be_disabled = True

        self._evaluate(context)

    def update_source_type(self, context):
        self.hide_disabled_inputs = False
        if self.source_type == "BLENDER":
            self.pasted_operator = self.pasted_operator
        elif self.source_type == "CUSTOM":
            self.ref_SN_OperatorNode = self.ref_SN_OperatorNode
        self._evaluate(context)

    ref_ntree: bpy.props.PointerProperty(
        type=bpy.types.NodeTree,
        name="Panel Node Tree",
        description="The node tree to select the operator from",
        poll=SN_ScriptingBaseNode.ntree_poll,
        update=SN_ScriptingBaseNode._evaluate,
    )

    source_type: bpy.props.EnumProperty(
        name="Source Type",
        description="Use a custom operator or a blender internal",
        items=[
            ("BLENDER", "Blender", "Blender", "BLENDER", 0),
            ("CUSTOM", "Custom", "Custom", "FILE_SCRIPT", 1),
        ],
        update=update_source_type,
    )

    ref_SN_OperatorNode: bpy.props.StringProperty(
        name="Custom Operator",
        description="The operator ran by this button",
        update=update_custom_operator,
    )

    def update_pasted_operator(self, context):
        self.reset_inputs()

        op = eval(self.pasted_operator.split("(")[0])
        op_rna = op.get_rna_type()
        self.pasted_name = op_rna.name
        self.create_inputs(op_rna)
        self._evaluate(context)

    pasted_operator: bpy.props.StringProperty(
        default="bpy.ops.sn.dummy_button_operator()", update=update_pasted_operator
    )

    pasted_name: bpy.props.StringProperty(default="Paste Operator")

    def update_hide_disabled_inputs(self, context):
        for inp in self.inputs:
            if inp.can_be_disabled and inp.disabled:
                inp.set_hide(self.hide_disabled_inputs)

    hide_disabled_inputs: bpy.props.BoolProperty(
        default=False,
        name="Hide Disabled Inputs",
        description="Hides the disabled inputs of this node",
        update=update_hide_disabled_inputs,
    )

    def evaluate(self, context):
        if self.source_type == "BLENDER":
            op_name = self.pasted_operator[8:].split("(")[0]
            code = f"op = {self.active_layout}.operator('{op_name}', text={self.inputs['Label'].python_value}, icon_value={self.inputs['Icon'].python_value}, emboss={self.inputs['Emboss'].python_value}, depress={self.inputs['Depress'].python_value})"

            op = eval(self.pasted_operator.split("(")[0])
            op_rna = op.get_rna_type()
            for inp in self.inputs:
                if inp.can_be_disabled and not inp.disabled:
                    for prop in op_rna.properties:
                        if (
                            self.version == 0
                            and (prop.name and prop.name == inp.name)
                            or (
                                not prop.name
                                and prop.identifier.replace("_", " ").title()
                                == inp.name
                            )
                        ) or (
                            self.version == 1
                            and inp.name.replace(" ", "_").lower() == prop.identifier
                        ):
                            code += "\n" + f"op.{prop.identifier} = {inp.python_value}"
            self.code = f"""
                        {self.indent(code, 6)}
                        {self.indent(self.outputs[0].python_value, 6)}
                        """

        else:
            if self.ref_ntree and self.ref_SN_OperatorNode in self.ref_ntree.nodes:
                node = self.ref_ntree.nodes[self.ref_SN_OperatorNode]
                code = f"op = {self.active_layout}.operator('sna.{node.operator_python_name}', text={self.inputs['Label'].python_value}, icon_value={self.inputs['Icon'].python_value}, emboss={self.inputs['Emboss'].python_value}, depress={self.inputs['Depress'].python_value})"

                for inp in self.inputs:
                    if inp.can_be_disabled and not inp.disabled:
                        for prop in node.properties:
                            if prop.name == inp.name:
                                code += (
                                    "\n" + f"op.{prop.python_name} = {inp.python_value}"
                                )
            else:
                code = f"op = {self.active_layout}.operator('sn.dummy_button_operator', text={self.inputs['Label'].python_value}, icon_value={self.inputs['Icon'].python_value}, emboss={self.inputs['Emboss'].python_value}, depress={self.inputs['Depress'].python_value})"

            self.code = f"""
                        {self.indent(code, 6)}
                        {self.indent(self.outputs[0].python_value, 6)}
                        """

    def draw_node(self, context, layout):
        row = layout.row(align=True)
        row.prop(self, "source_type", text="", icon_only=True)

        if self.source_type == "BLENDER":
            name = "Paste Operator"
            if self.pasted_operator:
                if self.pasted_name:
                    name = self.pasted_name
                elif len(self.pasted_operator.split(".")) > 2:
                    name = (
                        self.pasted_operator.split(".")[3]
                        .split("(")[0]
                        .replace("_", " ")
                        .title()
                    )
                else:
                    name = self.pasted_operator
            op = row.operator("sn.paste_operator", text=name, icon="PASTEDOWN")
            op.node_tree = self.node_tree.name
            op.node = self.name

        elif self.source_type == "CUSTOM":
            parent_tree = self.ref_ntree if self.ref_ntree else self.node_tree
            row.prop_search(
                self,
                "ref_ntree",
                bpy.data,
                "node_groups",
                text="",
                item_search_property="name",
            )
            subrow = row.row(align=True)
            subrow.enabled = self.ref_ntree != None
            subrow.prop_search(
                self,
                "ref_SN_OperatorNode",
                bpy.data.node_groups[parent_tree.name].node_collection(
                    "SN_OperatorNode"
                ),
                "refs",
                text="",
                item_search_property="name",
            )

            subrow = row.row()
            subrow.enabled = (
                self.ref_ntree != None
                and self.ref_SN_OperatorNode in self.ref_ntree.nodes
            )
            op = subrow.operator(
                "sn.find_node", text="", icon="RESTRICT_SELECT_OFF", emboss=False
            )
            op.node_tree = self.ref_ntree.name if self.ref_ntree else ""
            op.node = self.ref_SN_OperatorNode

        row.prop(
            self,
            "hide_disabled_inputs",
            text="",
            icon="HIDE_ON" if self.hide_disabled_inputs else "HIDE_OFF",
            emboss=False,
        )
