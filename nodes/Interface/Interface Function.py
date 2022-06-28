import bpy
from ..base_node import SN_ScriptingBaseNode
from ...utils import get_python_name, unique_collection_name



class SN_InterfaceFunctionNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_InterfaceFunctionNode"
    bl_label = "Function (Interface)"
    def layout_type(self, _): return "layout_function"
    is_trigger = True
    bl_width_default = 200
    node_color = "INTERFACE"

    def on_create(self, context):
        self.add_dynamic_interface_output()
        out = self.add_dynamic_data_output("Input")
        out.is_variable = True
        out.changeable = True


    def on_dynamic_socket_add(self, socket):
        if not socket.bl_idname == "SN_InterfaceSocket":
            sockets = []
            for out in self.outputs:
                if not out.bl_idname in ["SN_InterfaceSocket", "SN_DynamicInterfaceSocket"]:
                    sockets.append(out.name)
            socket["name"] = get_python_name(socket.name, "Input", lower=False)
            socket["name"] = unique_collection_name(socket.name, "Input", sockets[:-1], "_", includes_name=True)
            self.trigger_ref_update({ "added": socket })
        self._evaluate(bpy.context)

    def on_dynamic_socket_remove(self, index, is_output):
        first_index = 0
        for out in self.outputs:
            if out.bl_idname in ["SN_InterfaceSocket", "SN_DynamicInterfaceSocket"]:
                first_index += 1

        if index >= first_index:
            self.trigger_ref_update({ "removed": index - first_index + 1 })

    def on_socket_type_change(self, socket):
        if not socket.bl_idname == "SN_InterfaceSocket":
            self.trigger_ref_update({ "changed": socket })

    def on_socket_name_change(self, socket):
        if not socket.bl_idname == "SN_InterfaceSocket":
            sockets = []
            for out in self.outputs:
                if not out.bl_idname in ["SN_InterfaceSocket", "SN_DynamicInterfaceSocket"]:
                    sockets.append(out.name)
            socket["name"] = get_python_name(socket.name, "Input", lower=False)
            socket["name"] = unique_collection_name(socket.name, "Input", sockets[:-1], "_", includes_name=True)
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

        if index > 1:
            code = self.indent([out.python_value for out in self.outputs[:index-1]], 6)
        else:
            code = self.indent([out.python_value if out.name == 'Interface' else '' for out in self.outputs], 0)
        self.code = f"""
                    def {self.func_name}(layout_function, {out_names}):
                        {code if code.strip() else "pass"}
                    """

        for i, out in enumerate(self.outputs[index:-1]):
            out.python_value = out_values[i]


    def draw_node(self, context, layout):
        row = layout.row(align=True)
        row.prop(self, "name")
        row.operator("sn.find_referencing_nodes", text="", icon="VIEWZOOM").node = self.name
        row.operator("sn.copy_python_name", text="", icon="COPYDOWN").name = self.func_name