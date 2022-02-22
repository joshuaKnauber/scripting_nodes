import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_FunctionReturnNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_FunctionReturnNode"
    bl_label = "Function Return (Execute)"
    bl_width_default = 200

    def on_create(self, context):
        self.add_execute_input()
        out = self.add_dynamic_data_input("Output")
        out.is_variable = True
        out.changeable = True
        
        
    def on_dynamic_socket_add(self, socket):
        self.trigger_ref_update({ "added": socket })
    
    def on_dynamic_socket_remove(self, index, is_output):
        self.trigger_ref_update({ "removed": index })
        
    def on_socket_type_change(self, socket):
        self.trigger_ref_update({ "changed": socket })
        
    def on_socket_name_change(self, socket):
        self.trigger_ref_update({ "updated": socket })


    def evaluate(self, context):
        if len(self.inputs) > 2:
            returns = []
            for inp in self.inputs[1:-1]:
                returns.append(inp.python_value)
            returns = ", ".join(returns)
            self.code = f"return [{returns}]"
        else:
            self.code = f"return []"
    
    
    def draw_node(self, context, layout):
        layout.prop(self, "name")