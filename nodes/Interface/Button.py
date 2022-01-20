import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_ButtonNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_ButtonNode"
    bl_label = "Button"
    node_color = "INTERFACE"
    bl_width_default = 200

    def on_create(self, context):
        self.add_interface_input()
        self.add_string_input("Label")
        self.add_boolean_input("Emboss").default_value = True
        self.add_boolean_input("Depress")
        self.add_icon_input("Icon")
        
    
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
        

    def update_pasted_operator(self, context):
        self.reset_inputs()
        
        op = eval(self.pasted_operator.split("(")[0])
        op_rna = op.get_rna_type()
        self.pasted_name = op_rna.name
        self.create_inputs(op_rna)
    
    pasted_operator: bpy.props.StringProperty(default="bpy.ops.sn.dummy_button_operator()",
                                        update=update_pasted_operator)
    
    pasted_name: bpy.props.StringProperty(default="Paste Operator")
    

    def evaluate(self, context):
        op_name = self.pasted_operator[8:].split("(")[0]
        self.code = f"op = {self.active_layout}.operator('{op_name}', text={self.inputs['Label'].python_value}, icon_value={self.inputs['Icon'].python_value}, emboss={self.inputs['Emboss'].python_value}, depress={self.inputs['Depress'].python_value})"

        op = eval(self.pasted_operator.split("(")[0])
        op_rna = op.get_rna_type()
        for inp in self.inputs:
            if inp.can_be_disabled and not inp.disabled:
                for prop in op_rna.properties:
                    if prop.name == inp.name:
                        self.code += "\n" + f"op.{prop.identifier} = {inp.python_value}"


    def draw_node(self, context, layout):
        row = layout.row(align=True)
        op = row.operator("sn.paste_operator", text=self.pasted_name if self.pasted_operator else "Paste Operator", icon="PASTEDOWN")
        op.node_tree = self.node_tree.name
        op.node = self.name