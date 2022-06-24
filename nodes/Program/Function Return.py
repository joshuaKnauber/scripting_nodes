import bpy
from ..base_node import SN_ScriptingBaseNode
from ...utils import get_python_name, unique_collection_name



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
        socket["name"] = get_python_name(socket.name, "Output", lower=False)
        socket["name"] = unique_collection_name(socket.name, "Output", [inp.name for inp in self.inputs[1:-1]], "_", includes_name=True)
        self.trigger_ref_update({ "added": socket })
        self._evaluate(bpy.context)
    
    def on_dynamic_socket_remove(self, index, is_output):
        self.trigger_ref_update({ "removed": index })
        self._evaluate(bpy.context)
        
    def on_socket_type_change(self, socket):
        self.trigger_ref_update({ "changed": socket })
        self._evaluate(bpy.context)
        
    def on_socket_name_change(self, socket):
        socket["name"] = get_python_name(socket.name, "Output", lower=False)
        socket["name"] = unique_collection_name(socket.name, "Output", [inp.name for inp in self.inputs[1:-1]], "_", includes_name=True)
        self.trigger_ref_update({ "updated": socket })
        self._evaluate(bpy.context)


    def evaluate(self, context):
        if len(self.inputs) > 2:
            returns = []
            for inp in self.inputs[1:-1]:
                returns.append(inp.python_value)
            returns = ", ".join(returns)
            if len(self.inputs) == 3:
                self.code = f"return {returns}"
            else:
                self.code = f"return [{returns}]"
        else:
            self.code = f"return"
    
    
    def draw_node(self, context, layout):
        row = layout.row(align=True)
        row.prop(self, "name")
        row.operator("sn.find_referencing_nodes", text="", icon="VIEWZOOM").node = self.name