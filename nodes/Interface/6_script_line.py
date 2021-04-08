import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_ScriptLineInterfaceNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_ScriptLineInterfaceNode"
    bl_label = "Interface Script Line"
    # bl_icon = "GRAPH"
    bl_width_default = 200

    node_options = {
        "default_color": (0.3,0.3,0.3),
        "imperative_once": True
    }

    def on_create(self,context):
        inp = self.add_interface_input("Interface")
        inp.mirror_name = True
        inp.python_text = "sn_layout"
        self.add_string_input("Script Line")


    def draw_node(self,context,layout):
        layout.label(text="Use 'sn_layout' in your script!")


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

        if not code.strip():
            self.add_error("No Script Line","You haven't entered a script line for the node")

        return {
            "code": f"""
                    sn_layout = {touched_socket.links[0].from_node.what_layout(touched_socket.links[0].from_socket)}
                    try: {"exec("+code+")" if code.strip() else "pass"}
                    except Exception as exc: sn_handle_script_line_exception(exc, {code})
                    """
        }