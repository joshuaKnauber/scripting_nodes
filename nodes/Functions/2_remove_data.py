import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



class SN_RemoveDataNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_RemoveDataNode"
    bl_label = "Remove Blend Data"
    # bl_icon = "GRAPH"
    bl_width_default = 160

    node_options = {
        "default_color": (0.3,0.3,0.3),
    }
    
    
    current_data_type: bpy.props.StringProperty(default="")
    has_remove: bpy.props.BoolProperty()
    
    
    def add_function_inputs(self, data_type):
        self.remove_input_range(2)


        self.has_remove = False
        for data in bpy.data.bl_rna.properties:
            if "bl_rna" in dir(eval("bpy.data." + data.identifier)):
                if data.type == "COLLECTION" and type(data.fixed_type).bl_rna.identifier == data_type:
                    if "remove" in eval("bpy.data." + data.identifier).bl_rna.functions:
                        self.has_remove = True

                        for parameter in eval("bpy.data." + data.identifier).bl_rna.functions["remove"].parameters:
                            if not parameter.is_output:
                                self.add_input_from_prop(parameter)


    def on_link_insert(self, link):
        if link.to_socket == self.inputs[1] and link.from_socket.bl_idname == "SN_BlendDataSocket" and link.from_socket.subtype == "COLLECTION":
            if link.from_socket.data_type != self.current_data_type:
                self.inputs[1].default_text = link.from_socket.data_name
                self.inputs[1].data_type = link.from_socket.data_type
                self.current_data_type = link.from_socket.data_type
                self.add_function_inputs(link.from_socket.data_type)


    def on_create(self,context):
        self.add_execute_input("Remove Data")
        inp = self.add_blend_data_input("Blend Data")
        inp.subtype = "COLLECTION"
        self.add_execute_output("Execute").mirror_name = True


    def code_evaluate(self, context, touched_socket):
        
        if self.inputs[1].is_linked and self.has_remove:
            if touched_socket == self.inputs[0]:
                parameter = ""
                for inp in self.inputs[2:]:
                    parameter+=inp.variable_name + "=" + inp.code() + ", "
                return {
                    "code": f"""
                            remove_return_{self.uid} = {self.inputs[1].code()}.remove({parameter})
                            {self.outputs[0].code(7)}
                            """
                }
            else:
                return {"code": f"remove_return_{self.uid}"}

        elif self.has_remove:
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
            self.add_error("No remove function", "The blend data has no remove function", True)
            if touched_socket == self.inputs[0]:
                return {
                    "code": f"""
                            {self.outputs[0].code(7)}
                            """
                }

            else:
                return {"code": "None"}