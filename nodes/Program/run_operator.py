import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_OT_PasteOperator(bpy.types.Operator):
    bl_idname = "sn.paste_operator"
    bl_label = "Paste Operator"
    bl_description = "Pastes your copied operator in this node"
    bl_options = {"REGISTER","UNDO","INTERNAL"}
    
    node_name: bpy.props.StringProperty()
    
    def execute(self, context):
        if "bpy.ops." in context.window_manager.clipboard:
            context.space_data.node_tree.nodes[self.node_name].current_operator = context.window_manager.clipboard
        else:
            self.report({"WARNING"},message="Right-Click any button and click 'Copy Operator' to get a valid operator")
        return {"FINISHED"}




class SN_RunOperatorNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_RunOperatorNode"
    bl_label = "Run Operator"
    # bl_icon = "GRAPH"
    bl_width_default = 200

    node_options = {
        "default_color": (0.3,0.3,0.3),
    }
    
    def update_operator(self,context):
        ignore_props = ["RNA"]
        
        if self.current_operator:
            op = eval(self.current_operator.split("(")[0])
            
            self.label = "Operator (" + op.get_rna_type().name + ")"
            for prop in op.get_rna_type().bl_rna.properties:
                if not prop.name in ignore_props:
                    self.add_input_from_prop(prop)
        else:
            self.label = "Run Operator"
            for i in range(len(self.inputs)-1,0,-1):
                self.inputs.remove(self.inputs[i])
    
    current_operator: bpy.props.StringProperty(update=update_operator)

    def on_create(self,context):
        self.add_execute_input("Run Operator")
        self.add_execute_output("Execute")
        
    def draw_node(self,context,layout):
        if not self.current_operator:
            row = layout.row()
            row.scale_y = 1.5
            row.operator("sn.paste_operator",text="Paste Operator",icon="PASTEDOWN").node_name = self.name
        else:
            layout.operator("sn.reset_node",icon="UNLINKED").node = self.name

    def code_evaluate(self, context, touched_socket):

        operator = ""
        if self.current_operator:
            operator = self.current_operator.split("(")[0] + "("
        
            for inp in self.inputs:
                if inp.group == "DATA":
                    operator += f"{inp.variable_name}={inp.code()},"

            operator += ")"

        return {
            "code": f"""
                    {operator}
                    """
        }