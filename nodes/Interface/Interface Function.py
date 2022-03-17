import bpy
from ..base_node import SN_ScriptingBaseNode
from ...utils import get_python_name



class SN_InterfaceFunctionNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_InterfaceFunctionNode"
    bl_label = "Function (Interface)"
    layout_type = "layout_function"
    is_trigger = True
    bl_width_default = 200

    def on_create(self, context):
        self.add_interface_output()
        self.add_dynamic_interface_output()
        out = self.add_dynamic_data_output("Input")
        out.is_variable = True
        out.changeable = True


    def on_dynamic_socket_add(self, socket):
        if not socket.bl_idname == "SN_InterfaceSocket":
            self.trigger_ref_update({ "added": socket })

    def on_dynamic_socket_remove(self, index, is_output):
        if index+1 == len(self.outputs):
            self.trigger_ref_update({ "removed": index })
        elif self.outputs[index+1].bl_idname != "SN_InterfaceSocket":
            self.trigger_ref_update({ "removed": index })

    def on_socket_type_change(self, socket):
        if not socket.bl_idname == "SN_InterfaceSocket":
            self.trigger_ref_update({ "changed": socket })

    def on_socket_name_change(self, socket):
        if not socket.bl_idname == "SN_InterfaceSocket":
            self.trigger_ref_update({ "updated": socket })
        self._evaluate(bpy.context)


    @property
    def func_name(self):
        return f"sna_{get_python_name(self.name, 'func')}_{self.static_uid}"


    def evaluate(self, context):
        out_values = []
        index = 0
        for i, out in enumerate(self.outputs):
            if out.bl_idname != "SN_InterfaceSocket":
                index = i
                break
        for i, out in enumerate(self.outputs[index:-1]):
            out_values.append(get_python_name(out.name, f"parameter_{i}"))
        out_names = ", ".join(out_values)

        self.code = f"""
                    def {self.func_name}(layout_function, {out_names}):
                        pass
                        {self.indent([out.python_value for out in self.outputs[:index-1]], 6)}
                    """

        for i, out in enumerate(self.outputs[index:-1]):
            out.python_value = out_values[i]


    def draw_node(self, context, layout):
        layout.prop(self, "name")