import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup

def get_known_collection_functions():
    known_functions = {
        "Modifier": "bpy.types.ObjectModifiers.bl_rna.functions",
    }
    return known_functions

def get_known_functions():
    known_functions = {
    }
    return known_functions



class SN_RunFunctionOnNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_RunFunctionOnNode"
    bl_label = "Run Function On Data"
    # bl_icon = "GRAPH"
    bl_width_default = 180

    node_options = {
        "default_color": (0.3,0.3,0.3),
    }

    def get_functions(self, data_type, is_collection):
        self.function_collection.clear()
        if is_collection:
            if not data_type in get_known_collection_functions():
                has_functions = False
                for data in bpy.data.bl_rna.properties:
                    if "bl_rna" in dir(eval("bpy.data." + data.identifier)):
                        if data.type == "COLLECTION" and type(data.fixed_type).bl_rna.identifier == data_type:
                            has_functions = True
                            for function in eval("bpy.data." + data.identifier).bl_rna.functions:
                                item = self.function_collection.add()
                                item.name = function.identifier.replace("_", " ").title()
                                item.identifier = function.identifier

                if not has_functions:
                    try:
                        for function in eval("bpy.types." + data_type + "s").bl_rna.functions:
                            item = self.function_collection.add()
                            item.name = function.identifier.replace("_", " ").title()
                            item.identifier = function.identifier
                    except:
                        pass
            else:
                for function in eval(get_known_collection_functions()[data_type]):
                    item = self.function_collection.add()
                    item.name = function.identifier.replace("_", " ").title()
                    item.identifier = function.identifier

        else:
            if not data_type in get_known_functions():
                for function in eval("bpy.types." + data_type).bl_rna.functions:
                    item = self.function_collection.add()
                    item.name = function.identifier.replace("_", " ").title()
                    item.identifier = function.identifier

                functions = ["driver_add", "driver_remove", "keyframe_insert", "keyframe_delete"]
                for function in functions:
                    item = self.function_collection.add()
                    item.name = function.replace("_", " ").title()
                    item.identifier = function
            else:
                for function in eval(get_known_functions()[data_type]):
                    item = self.function_collection.add()
                    item.name = function.identifier.replace("_", " ").title()
                    item.identifier = function.identifier


        if not self.search_value in self.function_collection:
            self["search_value"] = ""

        if self.search_value != self.current_function:
            self.add_function_sockets(None)
        self.current_function = self.search_value


    def add_function_sockets(self, context):
        if not self.search_value in self.function_collection:
            self.remove_input_range(2)
            self.remove_output_range(1)

        if self.search_value in self.function_collection and self.search_value != self.current_function:
            self.remove_input_range(2)
            self.remove_output_range(1)
            if self.inputs[1].subtype == "COLLECTION":
                if not self.current_data_type in get_known_collection_functions():
                    has_parameters = False
                    for data in bpy.data.bl_rna.properties:
                        if data.type == "COLLECTION" and type(data.fixed_type).bl_rna.identifier == self.current_data_type:
                            parameters = eval("bpy.data." + data.identifier).bl_rna.functions[self.function_collection[self.search_value].identifier].parameters
                            has_parameters = True

                    if not has_parameters:
                        try:
                            parameters = eval("bpy.types." + self.current_data_type + "s").bl_rna.functions[self.function_collection[self.search_value].identifier].parameters
                        except:
                            parameters = []
                else:
                    parameters = eval(get_known_collection_functions()[self.current_data_type])[self.function_collection[self.search_value].identifier].parameters

            else:
                if not self.current_data_type in get_known_functions():
                    if self.function_collection[self.search_value].identifier in ["driver_add", "driver_remove", "keyframe_insert", "keyframe_delete"]:
                        parameters = []
                        if self.function_collection[self.search_value].identifier == "driver_add":
                            inp = self.add_string_input("Path")
                            inp.variable_name = "path"
                            inp.disableable = True
                            inp = self.add_integer_input("Index")
                            inp.set_default(-1)
                            inp.variable_name = "index"
                            inp.disableable = True
                            self.add_blend_data_output("Driver")

                        elif self.function_collection[self.search_value].identifier == "driver_remove":
                            inp = self.add_string_input("Path")
                            inp.variable_name = "path"
                            inp.disableable = True
                            inp = self.add_integer_input("Index")
                            inp.set_default(-1)
                            inp.variable_name = "index"
                            inp.disableable = True
                            self.add_boolean_output("Removed")

                        elif self.function_collection[self.search_value].identifier == "keyframe_insert":
                            inp = self.add_string_input("Path")
                            inp.variable_name = "data_path"
                            inp.disableable = True
                            inp = self.add_integer_input("Index")
                            inp.set_default(-1)
                            inp.variable_name = "index"
                            inp.disableable = True
                            inp = self.add_float_input("Frame")
                            inp.variable_name = "frame"
                            inp.disableable = True
                            inp = self.add_string_input("Group")
                            inp.variable_name = "group"
                            inp.disableable = True
                            self.add_boolean_output("Created")

                        elif self.function_collection[self.search_value].identifier == "keyframe_delete":
                            inp = self.add_string_input("Path")
                            inp.variable_name = "data_path"
                            inp.disableable = True
                            inp = self.add_integer_input("Index")
                            inp.set_default(-1)
                            inp.variable_name = "index"
                            inp.disableable = True
                            inp = self.add_float_input("Frame")
                            inp.variable_name = "frame"
                            inp.disableable = True
                            inp = self.add_string_input("Group")
                            inp.variable_name = "group"
                            inp.disableable = True
                            self.add_boolean_output("Removed")

                    else:
                        parameters = eval("bpy.types." + self.current_data_type).bl_rna.functions[self.function_collection[self.search_value].identifier].parameters

                else:
                    parameters = eval(get_known_functions()[self.current_data_type])[self.function_collection[self.search_value].identifier].parameters


            for parameter in parameters:
                if parameter.is_output:
                    self.add_output_from_prop(parameter)
                else:
                    inp = self.add_input_from_prop(parameter)
                    if not parameter.is_required:
                        inp.disableable = True

        self.current_function = self.search_value


    current_data_type: bpy.props.StringProperty()
    current_function: bpy.props.StringProperty()
    search_value: bpy.props.StringProperty(name="Function", update=add_function_sockets)
    function_collection: bpy.props.CollectionProperty(type=SN_GenericPropertyGroup)

    def on_link_insert(self, link):
        if link.to_socket == self.inputs[1] and link.from_socket.bl_idname == "SN_BlendDataSocket":
            if link.from_socket.data_type != self.current_data_type or self.inputs[1].subtype != link.from_socket.subtype:
                function = self.search_value
                self.search_value = ""
                self.inputs[1].data_type = link.from_socket.data_type
                self.inputs[1].subtype = link.from_socket.subtype
                self.inputs[1].default_text = link.from_socket.data_name
                self.current_data_type = link.from_socket.data_type
                self.get_functions(link.from_socket.data_type, link.from_socket.subtype=="COLLECTION")
                if function in self.function_collection:
                    self.search_value = function


    def on_create(self,context):
        self.add_execute_input("Run Function On")
        self.add_blend_data_input("Blend Data/Collection")
        self.add_execute_output("Execute").mirror_name = True


    def draw_node(self, context, layout):
        if len(self.function_collection):
            layout.prop_search(self, "search_value", self, "function_collection", text="")


    def code_evaluate(self, context, touched_socket):
        if self.search_value != "":
            if touched_socket == self.inputs[0]:
                parameter = ""
                for inp in self.inputs[2:]:
                    if inp.enabled:
                        parameter+=inp.variable_name + "=" + inp.code() + ", "

                return {
                    "code": f"""
                            run_function_on_{self.uid} = {self.inputs[1].code()}.{self.function_collection[self.search_value].identifier}({parameter})
                            {self.outputs[0].code(7)}
                            """
                }
            else:
                if len(self.outputs) > 2:
                    return {"code": f"run_function_on_{self.uid}[{self.outputs.find(touched_socket.name)-1}]"}
                else:
                    return {"code": f"run_function_on_{self.uid}"}

        else:
            self.add_error("No function selected", "You need to select a function")
            if touched_socket == self.inputs[0]:
                return {
                    "code": f"""
                            {self.outputs[0].code(7)}
                            """
                }

            else:
                return {"code": "None"}