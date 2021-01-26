import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_AddDataNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_AddDataNode"
    bl_label = "Create Blend Data"
    # bl_icon = "GRAPH"
    bl_width_default = 160

    node_options = {
        "default_color": (0.3,0.3,0.3),
    }
    
    
    current_data_type: bpy.props.StringProperty(default="")
    has_new: bpy.props.BoolProperty()


    def add_function_inputs(self, data_type):
        self.remove_input_range(2)

        self.has_new = False
        for data in bpy.data.bl_rna.properties:
            if "bl_rna" in dir(eval("bpy.data." + data.identifier)):
                if data.type == "COLLECTION" and type(data.fixed_type).bl_rna.identifier == data_type:
                    if "new" in eval("bpy.data." + data.identifier).bl_rna.functions:
                        self.has_new = True
                        if len(self.outputs) == 1:
                            self.add_blend_data_output("New Data")

                        for parameter in eval("bpy.data." + data.identifier).bl_rna.functions["new"].parameters:
                            if not parameter.is_output:
                                self.add_input_from_prop(parameter)

        if not self.has_new:
            if len(self.outputs) == 2:
                self.outputs.remove(self.outputs[1])


    def on_link_insert(self, link):
        if link.to_socket == self.inputs[1] and link.from_socket.bl_idname == "SN_BlendDataSocket" and link.from_socket.subtype == "COLLECTION":
            if link.from_socket.data_type != self.current_data_type:
                self.inputs[1].default_text = link.from_socket.data_name
                self.inputs[1].data_type = link.from_socket.data_type
                self.current_data_type = link.from_socket.data_type
                self.add_function_inputs(link.from_socket.data_type)
                if len(self.outputs) == 2:
                    out = self.outputs[1]
                    out.data_type = link.from_socket.data_type
                    for link in self.outputs[1].links:
                        link.to_socket.node.on_link_insert(link)


    def on_create(self,context):
        self.add_execute_input("Execute").mirror_name = True
        inp = self.add_blend_data_input("Blend Data")
        inp.subtype = "COLLECTION"
        self.add_execute_output("Execute")


    def code_evaluate(self, context, touched_socket):
        
        if self.inputs[1].is_linked and self.has_new:
            if touched_socket == self.inputs[0]:
                parameter = ""
                for inp in self.inputs[2:]:
                    parameter+=inp.variable_name + "=" + inp.code() + ", "
                return {
                    "code": f"""
                            new_return_{self.uid} = {self.inputs[1].code()}.new({parameter})
                            {self.outputs[0].code(7)}
                            """
                }
            else:
                return {"code": f"new_return_{self.uid}"}

        elif self.has_new:
            self.add_error("No blend data", "The blend data input is not connected", True)
            if touched_socket == self.inputs[0]:
                return {
                    "code": f"""
                            {self.outputs[0].code(7)}
                            """
                }

            else:
                return {"code": "None"}

        else:
            self.add_error("No Create Function", "The blend data has no create function", True)
            if touched_socket == self.inputs[0]:
                return {
                    "code": f"""
                            {self.outputs[0].code(7)}
                            """
                }

            else:
                return {"code": "None"}