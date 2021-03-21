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
    
    
    has_new: bpy.props.BoolProperty()


    def add_function_inputs(self, data_type):
        self.remove_input_range(2)
        self.remove_output_range(1)

        self.has_new = False
        if "new" in eval("bpy.types." + data_type).bl_rna.functions:
            self.has_new = True
            for parameter in eval("bpy.types." + data_type).bl_rna.functions["new"].parameters:
                if not parameter.is_output:
                    self.add_input_from_prop(parameter)
                else:
                    self.add_output_from_prop(parameter)

        if not self.has_new:
            if len(self.outputs) == 2:
                self.outputs.remove(self.outputs[1])


    def on_link_insert(self, link):
        if link.to_socket == self.inputs[1] and link.from_socket.bl_idname == "SN_BlendDataSocket" and link.from_socket.subtype == "COLLECTION":
            if link.from_socket.data_type_collection != self.inputs[1].data_type_collection or link.from_socket.data_type != self.inputs[1].data_type:
                self.inputs[1].default_text = link.from_socket.data_name
                self.inputs[1].data_type = link.from_socket.data_type
                self.inputs[1].data_type_collection = link.from_socket.data_type_collection
                if link.from_socket.data_type_collection:
                    self.add_function_inputs(link.from_socket.data_type_collection)
                else:
                    self.add_function_inputs(link.from_socket.data_type)

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