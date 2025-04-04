import bpy
from ..base_node import SN_ScriptingBaseNode
from ...utils import get_python_name, unique_collection_name



class SN_FunctionNode(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_FunctionNode"
    bl_label = "Function (Execute)"
    is_trigger = True
    bl_width_default = 200

    def on_create(self, context):
        self.add_execute_output()
        out = self.add_dynamic_data_output("Input")
        out.is_variable = True
        out.changeable = True


    def on_dynamic_socket_add(self, socket):
        socket["name"] = get_python_name(socket.name, "Input", lower=False)
        socket["name"] = unique_collection_name(socket.name, "Input", [out.name for out in self.outputs[1:-1]], "_", includes_name=True)
        socket.python_value = socket.name
        if hasattr(socket, "size_editable"):
            socket.size_editable = True
        self.trigger_ref_update({ "added": socket })
        self._evaluate(bpy.context)


    def on_dynamic_socket_remove(self, index, is_output):
        self.trigger_ref_update({ "removed": index })
        self._evaluate(bpy.context)


    def on_socket_type_change(self, socket):
        if socket.bl_label == "Enum" or socket.bl_label == "Enum Set":
            socket.subtype = "CUSTOM_ITEMS"
        elif hasattr(socket, "size_editable"):
            socket.size_editable = True
        self.trigger_ref_update({ "changed": socket })
        self._evaluate(bpy.context)


    def on_socket_name_change(self, socket):
        socket["name"] = get_python_name(socket.name, "Input", lower=False)
        socket["name"] = unique_collection_name(socket.name, "Input", [out.name for out in self.outputs[1:-1]], "_", includes_name=True)
        socket.python_value = socket.name
        self.trigger_ref_update({ "updated": socket })
        self._evaluate(bpy.context)


    def update_fixed_name(self, context):
        self.trigger_ref_update()
        self._evaluate(context)
        
    fixed_func_name: bpy.props.StringProperty(default="",
                                        name="Fixed Name",
                                        description="A fixed python name that will be used for this function",
                                        update=update_fixed_name)


    @property
    def func_name(self):
        if self.fixed_func_name:
            return self.fixed_func_name
        return f"sna_{get_python_name(self.name, 'func')}_{self.static_uid}"

    def evaluate(self, context):
        out_values = []
        for i, out in enumerate(self.outputs[1:-1]):
            out_values.append(get_python_name(out.name, f"parameter_{i}", lower=False))
        out_names = ", ".join(out_values)
            
        self.code = f"""
                    def {self.func_name}({out_names}):
                        {self.indent(self.outputs[0].python_value, 6) if self.outputs[0].python_value else 'pass'}
                    """

        for i, out in enumerate(self.outputs[1:-1]):
            out.python_value = out_values[i]
    
    
    def draw_node(self, context, layout):
        row = layout.row(align=True)
        row.prop(self, "name")
        op = row.operator("sn.find_referencing_nodes", text="", icon="VIEWZOOM")
        op.node = self.name
        op.add_node = "SN_RunFunctionNode"
        row.operator("sn.copy_python_name", text="", icon="COPYDOWN").name = self.func_name
        
    def draw_node_panel(self, context, layout):
        layout.prop(self, "fixed_func_name")