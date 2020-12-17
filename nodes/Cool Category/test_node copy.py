import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_OtherTestNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_OtherTestNode"
    bl_label = "Other Test"
    bl_icon = "GRAPH"
    
    node_options = {
        "default_color": (0.3,0.3,0.3),
        "starts_tree": True,
        "import_once": True,
        "evaluate_once": False,
        "register_once": True,
        "unregister_once": False,
        "imperative_once": False,
    }

    def on_create(self,context):
        self.add_execute_output("Program")
        self.add_execute_output("Program")
        self.add_execute_output("Program")
        self.add_string_input("print 1")
        self.add_string_input("print 2")
        self.add_string_input("print 3")
        
    def code_imports(self, context, main_tree):
        return {
            "code": f"""
                    import bpy
                    """
        }
        
    def code_imperative(self, context, main_tree):
        return {
            "code": f"""
                    # hello im imperative
                    # {self.inputs[0].value}
                    """
        }

    def code_evaluate(self, context, main_tree, touched_socket):
        strings = []
        for inp in self.inputs:
            if inp.sn_type == "STRING":
                strings.append("# "+inp.value)
                
        programs = []
        for out in self.outputs:
            if out.sn_type == "EXECUTE":
                programs.append(out.block(0))
                
        self.add_error("test error", "test description gesg psjepg jpsejg psejpg jpseg jpsej gposjegp jsepg jpes", True)
                
        return {
            "code": f"""
                    def test():
                        # {self.node_tree.name}
                        print("{self.inputs[0].value}")
                        {self.outputs[0].block(6)}
                        {self.list_blocks(programs, 6)}
                        {"# "+self.inputs[0].value if self.inputs[0].value else ""}
                        {self.list_values(strings, 6)}
                        pass # again
                        
                    """
        }