import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_ButtonNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_ButtonNode"
    bl_label = "Button"
    node_color = "INTERFACE"
    bl_width_default = 200

    def on_create(self, context):
        self.add_interface_input()
        self.add_string_input("Label").default_value = "My Button"
        self.add_boolean_input("Emboss").default_value = True
        self.add_boolean_input("Depress")
        self.add_icon_input("Icon")
        
        
    def on_ref_update(self, node, data=None):
        if node.node_tree == self.custom_operator_ntree and node.name == self.ref_SN_OperatorNode:
            pass
        
    
    def reset_inputs(self):
        """ Remove all operator inputs """
        for i in range(len(self.inputs)-1, -1, -1):
            inp = self.inputs[i]
            if inp.can_be_disabled:
                self.inputs.remove(inp)
    
    
    def create_inputs(self, op_rna):
        """ Create inputs for operator """
        for prop in op_rna.properties:
            if not prop.identifier in ["rna_type", "settings"]:
                inp = self.add_input_from_property(prop)
                if inp:
                    inp.can_be_disabled = True
                    inp.disabled = not prop.is_required
    
    
    def update_custom_operator(self, context):
        """ Updates the nodes settings when a new parent panel is selected """
        self.reset_inputs()
        if self.custom_operator_ntree and self.ref_SN_OperatorNode in self.custom_operator_ntree.nodes:
            parent = self.custom_operator_ntree.nodes[self.ref_SN_OperatorNode]
            for prop in parent.properties:
                pass
        self._evaluate(context)
        
    def update_source_type(self, context):
        self.hide_disabled_inputs = False
        if self.source_type == "BLENDER":
            self.pasted_operator = self.pasted_operator
        elif self.source_type == "CUSTOM":
            self.ref_SN_OperatorNode = self.ref_SN_OperatorNode
        self._evaluate(context)
    
    custom_operator_ntree: bpy.props.PointerProperty(type=bpy.types.NodeTree,
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
        
        op = eval(self.pasted_operator.split("(")[0])
        op_rna = op.get_rna_type()
        self.pasted_name = op_rna.name
        self.create_inputs(op_rna)
    
    pasted_operator: bpy.props.StringProperty(default="bpy.ops.sn.dummy_button_operator()",
                                        update=update_pasted_operator)
    
    pasted_name: bpy.props.StringProperty(default="Paste Operator")
    
    
    def udpate_hide_disabled_inputs(self, context):
        for inp in self.inputs:
            if inp.can_be_disabled:
                inp.set_hide(self.hide_disabled_inputs)
    
    hide_disabled_inputs: bpy.props.BoolProperty(default=False,
                                        name="Hide Disabled Inputs",
                                        description="Hides the disabled inputs of this node",
                                        update=udpate_hide_disabled_inputs)
    

    def evaluate(self, context):
        if self.source_type == "BLENDER":
            op_name = self.pasted_operator[8:].split("(")[0]
            self.code = f"op = {self.active_layout}.operator('{op_name}', text={self.inputs['Label'].python_value}, icon_value={self.inputs['Icon'].python_value}, emboss={self.inputs['Emboss'].python_value}, depress={self.inputs['Depress'].python_value})"

            op = eval(self.pasted_operator.split("(")[0])
            op_rna = op.get_rna_type()
            for inp in self.inputs:
                if inp.can_be_disabled and not inp.disabled:
                    for prop in op_rna.properties:
                        if prop.name == inp.name:
                            self.code += "\n" + f"op.{prop.identifier} = {inp.python_value}"
        
        else:
            pass


    def draw_node(self, context, layout):
        row = layout.row(align=True)
        
        if self.source_type == "BLENDER":
            op = row.operator("sn.paste_operator", text=self.pasted_name if self.pasted_operator else "Paste Operator", icon="PASTEDOWN")
            op.node_tree = self.node_tree.name
            op.node = self.name
        
        elif self.source_type == "CUSTOM":
            parent_tree = self.custom_operator_ntree if self.custom_operator_ntree else self.node_tree
            row.prop_search(self, "custom_operator_ntree", bpy.data, "node_groups", text="")
            subrow = row.row(align=True)
            subrow.enabled = self.custom_operator_ntree != None
            subrow.prop_search(self, "ref_SN_OperatorNode", bpy.data.node_groups[parent_tree.name].node_collection("SN_OperatorNode"), "refs", text="")

        row.prop(self, "source_type", text="", icon_only=True)
        row.prop(self, "hide_disabled_inputs", text="", icon="HIDE_ON" if self.hide_disabled_inputs else "HIDE_OFF")