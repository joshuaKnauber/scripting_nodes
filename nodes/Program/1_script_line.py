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

    def on_create(self,context):
        self.add_execute_input("Script Line")
        self.add_string_input("Script Line")
        self.add_execute_output("Execute").mirror_name = True

        
    def code_imperative(self, context):
        return {
            "code": f"""
                    def sn_handle_script_line_exception(exc, line):
                        print("# # # # # # # # SCRIPT LINE ERROR # # # # # # # #")
                        print("Line:", line)
                        raise exc
                    """
        }


    def code_evaluate(self, context, touched_socket):
        code = self.inputs[1].code()

        if not code:
            self.add_error("No Script Line","You haven't entered a script line for the node")

        return {
            "code": f"""
                    try: {"exec("+code+")" if code.strip() else "pass"}
                    except Exception as exc: sn_handle_script_line_exception(exc, {code})
                    {self.outputs[0].code(5)}
                    """
        }