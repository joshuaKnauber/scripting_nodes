import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_ScriptLineNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_ScriptLineNode"
    bl_label = "Script Line"
    # bl_icon = "GRAPH"
    bl_width_default = 200

    node_options = {
        "default_color": (0.3,0.3,0.3),
        "imperative_once": True
    }

    script_line: bpy.props.StringProperty(default="",
                                          name="Script Line",
                                          description="The python line you want to run")

    def on_create(self,context):
        self.add_execute_input("Execute")
        self.add_execute_output("Execute")


    def draw_node(self,context,layout):
        row = layout.row(align=True)
        row.prop(self, "script_line", text="")
        row.operator("sn.get_python_name",text="",icon="UV_SYNC_SELECT")
        
        
    def code_imperative(self, context):
        return {
            "code": f"""
                    def sn_handle_script_line_exception(exc):
                        print("# # # # # # # # SCRIPT LINE ERROR # # # # # # # #")
                        print("Line: {self.script_line}")
                        raise exc
                    """
        }


    def code_evaluate(self, context, touched_socket):
        
        if not self.script_line:
            self.add_error("No Script Line","You haven't entered a script line for the node")
        
        return {
            "code": f"""
                    try: {self.script_line if self.script_line else "pass"}
                    except Exception as exc: sn_handle_script_line_exception(exc)
                    {self.outputs[0].code(5)}
                    """
        }