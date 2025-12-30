import bpy
from ..base_node import SN_ScriptingBaseNode
from ...utils import get_python_name, unique_collection_name



class SN_FunctionReturnNode(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_FunctionReturnNode"
    bl_label = "Function Return (Execute)"
    bl_width_default = 200

    def on_create(self, context):
        self.add_execute_input()
        out = self.add_dynamic_data_input("Output")
        out.is_variable = True
        out.changeable = True
        
        
    def on_dynamic_socket_add(self, socket):
        current_name = socket.name
        new_name = get_python_name(current_name, "Output", lower=False)
        new_name = unique_collection_name(new_name, "Output", [inp.name for inp in self.inputs], "_", includes_name=True)
        if new_name != current_name:
            socket.set_name_silent(new_name)
        self.trigger_ref_update({ "added": socket })
        self._evaluate(bpy.context)
    
    def on_dynamic_socket_remove(self, index, is_output):
        self.trigger_ref_update({ "removed": index })
        self._evaluate(bpy.context)
        
    def on_socket_type_change(self, socket):
        self.trigger_ref_update({ "changed": socket })
        self._evaluate(bpy.context)
        
    def on_socket_name_change(self, socket):
        # Prevent recursion
        storage_key = f"_socket_updating_name_{id(socket)}"
        if self.get(storage_key, False):
            return
        
        # Get the current name value from stored value (set by update_socket_name)
        name_storage_key = f"_socket_current_name_{id(socket)}"
        current_name = self.get(name_storage_key, socket.name)  # Fallback to socket.name if not stored
        
        new_name = get_python_name(current_name, "Output", lower=False)
        new_name = unique_collection_name(new_name, "Output", [inp.name for inp in self.inputs], "_", includes_name=True)
        if new_name != current_name:
            socket.set_name_silent(new_name)
        self.trigger_ref_update({ "updated": socket, "new_name": new_name })
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