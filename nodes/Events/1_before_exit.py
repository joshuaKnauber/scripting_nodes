import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup
from ...compiler.compiler import get_module



class SN_BeforeExitNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_BeforeExitNode"
    bl_label = "On Exit"
    # bl_icon = "GRAPH"
    bl_width_default = 160

    node_options = {
        "default_color": (0.2,0.2,0.2),
        "starts_tree": True,
        "import_once": True
    }


    def on_create(self,context):
        self.add_execute_output("On Exit")


    def draw_node(self,context,layout):
        row = layout.row()
        row.scale_y = 1.2
        row.enabled = get_module(self.addon_tree) != None
        op = row.operator("sn.test_event",text="Run Event",icon="PLAY")
        op.node = self.name
        op.func_name = f"before_exit_handler_{self.uid}"


    def code_imports(self, context):
        return {
            "code": f"""
                    import atexit
                    """
        }


    def code_imperative(self, context):
        return {
            "code": f"""
                    def before_exit_handler_{self.uid}(dummy):
                        print(dummy)
                        {self.outputs[0].code(6) if self.outputs[0].code().strip() else "pass"}
                    """
        }

    
    def code_register(self, context):
        return {
            "code": f"""
                    atexit.register(before_exit_handler_{self.uid})
                    """
        }


    def code_unregister(self, context):
        return {
            "code": f"""
                    atexit.unregister(before_exit_handler_{self.uid})
                    """
        }