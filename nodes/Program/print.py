import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_PrintNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_PrintNode"
    bl_label = "Print"
    # bl_icon = "GRAPH"
    bl_width_default = 160

    node_options = {
        "default_color": (0.3,0.3,0.3),
    }

    has_report: bpy.props.BoolProperty(default=False)
    is_report: bpy.props.BoolProperty(default=False,name="Report",description="Show a report message instead of printing")
    report_type: bpy.props.EnumProperty(name="Report Types",items=[("INFO","Info","Info"),("WARNING","Warning","Warning"),("ERROR","Error","Error")])

    def on_create(self,context):
        self.add_execute_input("Print")
        self.add_execute_output("Execute").mirror_name = True
        self.add_string_input("Content").removable = True
        self.add_dynamic_string_input("Content")


    def on_node_update(self):
        self.has_report = False
        if len(self.inputs):
            if len(self.inputs[0].links):
                if self.what_start_idname() == "SN_OperatorNode":
                    self.has_report = True


    def draw_node(self, context, layout):
        if self.has_report:
            layout.prop(self,"is_report")
            if self.is_report:
                layout.prop(self,"report_type",text="")


    def code_evaluate(self, context, touched_socket):

        if self.has_report and self.is_report:
            return {
                "code": f"""
                        try: self.report({"{'" + self.report_type + "'}"}, message={self.inputs["Content"].by_name(separator='+" "+')})
                        except: print("Serpens - Can't report in this context!")
                        {self.outputs[0].code(6)}
                        """
            }
            
        if self.addon_tree.doing_export:
            return {
                "code": f"""
                        print({self.inputs["Content"].by_name(separator=", ")})
                        {self.outputs[0].code(6)}
                        """
            }
        
        else:
            return {
                "code": f"""
                        sn_print("{self.addon_tree.name}",{self.inputs["Content"].by_name(separator=", ")})
                        {self.outputs[0].code(6)}
                        """
            }