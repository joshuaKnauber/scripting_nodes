import bpy
import json
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup
from ...interface.menu.rightclick import construct_from_property



class SN_OT_PasteOperator(bpy.types.Operator):
    bl_idname = "sn.paste_operator"
    bl_label = "Paste Operator"
    bl_description = "Pastes your copied operator in this node"
    bl_options = {"REGISTER","UNDO","INTERNAL"}
    
    node_name: bpy.props.StringProperty()
    
    def execute(self, context):
        if "bpy.ops." in context.window_manager.clipboard:
            context.space_data.node_tree.nodes[self.node_name].operator = context.window_manager.clipboard
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
    
    
    def add_inputs_from_internal(self):
        rna = eval(self.operator.split("(")[0] + ".get_rna_type()")
        for prop in rna.properties:
            if not prop.name == "RNA":
                self.add_input_from_prop(prop).disableable = True
    
    
    def update_operator(self,context):
        if self.operator:
            self.add_inputs_from_internal()
        else:
            self.remove_input_range(1)
            
            
    def update_inputs_from_operator(self, index=-1):
        props = self.addon_tree.sn_nodes["SN_OperatorNode"].items[self.custom_operator].node().operator_properties

        # length is higher -> at least one socket got added
        if len(props) > len(self.inputs)-1:
            if len(self.inputs) == 1:
                for prop in props:
                    data = json.loads(construct_from_property("self",prop))["property"]
                    self.add_input_from_data(data).disableable = True
            else:
                data = json.loads(construct_from_property("self",props[-1]))["property"]
                self.add_input_from_data(data).disableable = True
            
        # length is lower -> socket got removed
        elif len(props) < len(self.inputs)-1:
            did_remove = False
            for i, prop in enumerate(props):
                if not self.inputs[i+1].name == prop.name:
                    self.inputs.remove(self.inputs[i+1])
                    did_remove = True
                    break
            if not did_remove:
                self.inputs.remove(self.inputs[-1])
                
        elif index >= 0:
            prop = props[index]
            inp = self.inputs[index+1]
            self.inputs.remove(inp)
            data = json.loads(construct_from_property("self",prop))["property"]
            self.add_input_from_data(data).disableable = True
            self.inputs.move(len(self.inputs)-1,index+1)

    
    def update_custom_operator(self,context):
        self.remove_input_range(1)
        if self.custom_operator and self.custom_operator in self.addon_tree.sn_nodes["SN_OperatorNode"].items:
            self.update_inputs_from_operator()
    
    
    def update_use_internal(self,context):
        self.operator = ""
        self.custom_operator = ""
    
    
    operator: bpy.props.StringProperty(update=update_operator)
    use_internal: bpy.props.BoolProperty(name="Use Internal",
                                         description="Use blenders internal operators instead of your custom ones",
                                         update=update_use_internal)
    
    custom_operator: bpy.props.StringProperty(name="Custom Operator",
                                              description="Your custom operator",
                                              update=update_custom_operator)
    
    call_invoke: bpy.props.BoolProperty(name="Call Invoke",
                                        description="Calls the invoke function of the operator",
                                        default=True)
    
    
    def on_create(self,context):
        self.add_required_to_collection(["SN_OperatorNode"])
        self.add_execute_input("Run Operator")
        self.add_execute_output("Execute")
    
        
    def draw_node(self,context,layout):
        row = layout.row(align=True)
        if self.use_internal:
            if not self.operator:
                row.operator("sn.paste_operator",text="Paste Operator",icon="PASTEDOWN").node_name = self.name
            else:
                row.operator("sn.reset_property_node",icon="UNLINKED").node = self.name
            row.prop(self,"use_internal",text="",icon="BLENDER",invert_checkbox=True)
        elif "SN_OperatorNode" in self.addon_tree.sn_nodes:
            row.prop_search(self,"custom_operator",self.addon_tree.sn_nodes["SN_OperatorNode"],"items",text="",icon="VIEWZOOM")
            row.prop(self,"use_internal",text="",icon_value=bpy.context.scene.sn_icons[ "serpens" ].icon_id)
            
        layout.prop(self,"call_invoke")


    def code_evaluate(self, context, touched_socket):
        operator = ""
        
        if self.use_internal:
            if self.operator:
                operator = self.operator.split("(")[0] + "("
                if self.call_invoke:
                    operator += "\"INVOKE_DEFAULT\","
                
        else:
            if self.custom_operator and self.custom_operator in self.addon_tree.sn_nodes["SN_OperatorNode"].items:
                item = self.addon_tree.sn_nodes["SN_OperatorNode"].items[self.custom_operator]
                operator = "bpy.ops.sna." + item.identifier + "("
            
        if operator:
            for inp in self.inputs:
                if inp.group == "DATA" and inp.enabled:
                    operator += f"{inp.variable_name}={inp.code()},"

            operator += ")"

        return {
            "code": f"""
                    {operator}
                    """
        }