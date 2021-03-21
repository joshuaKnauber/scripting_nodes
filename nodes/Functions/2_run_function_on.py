import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup
from ..Blend_Data.a_get_data_pointers import get_known_types



class SN_RunFunctionOnNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_RunFunctionOnNode"
    bl_label = "Run Function On Data"
    # bl_icon = "GRAPH"
    bl_width_default = 180

    node_options = {
        "default_color": (0.3,0.3,0.3),
    }

    def get_cats(self, context):
        return eval(self.categories)

    def update_cats(self, context):
        index = 1 if self.use_execute else 0
        data_type = self.inputs[index].data_type_collection if self.inputs[index].data_type_collection else self.inputs[index].data_type
        types = get_known_types()[data_type][self.category_enum]
        types.insert(0, (data_type, self.inputs[index].data_name, ""))
        self.types = str(types)
        self.define_type = data_type

    def get_types(self, context):
        return eval(self.types)

    def update_type(self, context):
        self.search_value = ""
        self.current_function = ""
        if self.use_execute:
            self.remove_input_range(2)
            self.remove_output_range(1)
        else:
            self.remove_input_range(1)
            self.outputs.clear()
        index = 1 if self.use_execute else 0
        self.get_functions(self.define_type, self.inputs[index].subtype == "COLLECTION")


    def get_functions(self, data_type, is_collection):
        self.function_collection.clear()
        if is_collection:
            try:
                for function in eval("bpy.types." + data_type).bl_rna.functions:
                    item = self.function_collection.add()
                    item.name = function.identifier.replace("_", " ").title()
                    item.identifier = function.identifier
            except:
                pass

        else:
            for function in eval("bpy.types." + data_type).bl_rna.functions:
                item = self.function_collection.add()
                item.name = function.identifier.replace("_", " ").title()
                item.identifier = function.identifier

            functions = ["driver_add", "driver_remove", "keyframe_insert", "keyframe_delete"]
            for function in functions:
                item = self.function_collection.add()
                item.name = function.replace("_", " ").title()
                item.identifier = function

        if not self.search_value in self.function_collection:
            self["search_value"] = ""

        if self.search_value != self.current_function:
            self.add_function_sockets(None)
        self.current_function = self.search_value


    def add_function_sockets(self, context):
        if not self.search_value in self.function_collection:
            if self.use_execute:
                self.remove_input_range(2)
                self.remove_output_range(1)
            else:
                self.remove_input_range(1)
                self.outputs.clear()

        index = 1 if self.use_execute else 0
        data_type = self.inputs[index].data_type_collection if self.inputs[index].data_type_collection else self.inputs[index].data_type
        if self.types != "[]":
            data_type = self.define_type

        if self.search_value in self.function_collection and self.search_value != self.current_function:
            if self.use_execute:
                self.remove_input_range(2)
                self.remove_output_range(1)
            else:
                self.remove_input_range(1)
                self.outputs.clear()

            if self.inputs[index].subtype == "COLLECTION":
                try:
                    parameters = eval("bpy.types." + data_type).bl_rna.functions[self.function_collection[self.search_value].identifier].parameters
                except:
                    parameters = []

            else:
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
                    parameters = eval("bpy.types." + data_type).bl_rna.functions[self.function_collection[self.search_value].identifier].parameters


            for parameter in parameters:
                if parameter.is_output:
                    self.add_output_from_prop(parameter)
                else:
                    inp = self.add_input_from_prop(parameter)
                    if not parameter.is_required:
                        inp.disableable = True

        self.current_function = self.search_value

    def update_execute(self, context):
        if self.use_execute:
            inp = self.add_execute_input("Run Function On")
            self.inputs.move(len(self.inputs)-1, 0)
            out = self.add_execute_output("Execute").mirror_name = True
            self.outputs.move(len(self.outputs)-1, 0)
        else:
            self.inputs.remove(self.inputs[0])
            self.outputs.remove(self.outputs[0])


    current_data_type: bpy.props.StringProperty()
    current_function: bpy.props.StringProperty()
    search_value: bpy.props.StringProperty(name="Function", update=add_function_sockets)
    function_collection: bpy.props.CollectionProperty(type=SN_GenericPropertyGroup)
    use_execute: bpy.props.BoolProperty(default=True, name="Use Execute", description="Function will run on every output access if disabled", update=update_execute)
    types: bpy.props.StringProperty(default="[]")
    categories: bpy.props.StringProperty(default="[]")
    category_enum: bpy.props.EnumProperty(items=get_cats, name="Category", update=update_cats)
    define_type: bpy.props.EnumProperty(items=get_types, name="Type", description="The type of the blend data you are trying to get from", update=update_type)


    def on_link_insert(self, link):
        index = 1 if self.use_execute else 0
        socket = link.from_socket
        if link.to_socket == self.inputs[index] and socket.bl_idname == "SN_BlendDataSocket":
            if socket.data_type == "":
                self.search_value = ""
                self.function_collection.clear()
                self.inputs[index].data_type = ""
                self.inputs[index].data_type_collection = ""
                self.inputs[index].subtype = "NONE"
                self.inputs[index].default_text = "Blend Data/Collection"
                self.current_data_type = ""
                self.types = "[]"
                self.categories = "[]"
                self.add_function_sockets(None)

            elif self.inputs[index].data_type != socket.data_type or self.inputs[index].subtype != socket.subtype or self.inputs[index].data_type_collection != socket.data_type_collection:
                function = self.search_value
                self.search_value = ""
                self.inputs[index].data_type = socket.data_type
                self.inputs[index].data_type_collection = socket.data_type_collection
                self.inputs[index].subtype = socket.subtype
                self.inputs[index].default_text = socket.data_name
                self.current_data_type = socket.data_type

                self.types = "[]"
                self.categories = "[]"
                types = []
                data_type = socket.data_type_collection if socket.data_type_collection else socket.data_type
                if data_type in get_known_types():
                    if type(get_known_types()[data_type]) == dict:
                        cats = []
                        for cat in get_known_types()[data_type]:
                            cats.append((cat, cat, ""))
                        self.categories = str(cats)
                        types = get_known_types()[data_type][self.category_enum]
                    else:
                        types = get_known_types()[data_type]

                else:
                    try:
                        for bpy_type in dir(bpy.types):
                            if eval("bpy.types." + data_type) in eval("bpy.types." + bpy_type).__bases__:
                                name = eval("bpy.types." + bpy_type).bl_rna.name if eval("bpy.types." + bpy_type).bl_rna.name else bpy_type
                                types.append((bpy_type, name, eval("bpy.types." + bpy_type).bl_rna.description))
                    except:
                        types = []

                if types:
                    types.insert(0, (data_type, socket.data_name, ""))
                    self.types = str(types)
                    self.define_type = data_type

                self.get_functions(data_type, socket.subtype=="COLLECTION")
                if function in self.function_collection:
                    self.search_value = function


    def on_create(self,context):
        self.add_execute_input("Run Function On")
        self.add_blend_data_input("Blend Data/Collection")
        self.add_execute_output("Execute").mirror_name = True


    def draw_node(self, context, layout):
        layout.prop(self, "use_execute")

        if self.categories != "[]":
            layout.prop(self, "category_enum", text="")
        if self.types != "[]":
            layout.prop(self, "define_type", text="")

        if len(self.function_collection):
            layout.prop_search(self, "search_value", self, "function_collection", text="")


    def code_evaluate(self, context, touched_socket):
        if self.search_value != "":
            if self.use_execute:
                if touched_socket == self.inputs[0]:
                    parameter = ""
                    for inp in self.inputs[2:]:
                        if inp.enabled:
                            parameter+=inp.variable_name + "=" + inp.code() + ", "

                    return {
                        "code": f"""
                                run_function_on_{self.uid} = {self.inputs[1].code()}.{self.function_collection[self.search_value].identifier}({parameter})
                                {self.outputs[0].code(8)}
                                """
                    }
                else:
                    if len(self.outputs) > 2:
                        return {"code": f"run_function_on_{self.uid}[{self.outputs.find(touched_socket.name)-1}]"}
                    else:
                        return {"code": f"run_function_on_{self.uid}"}
            else:
                parameter = ""
                for inp in self.inputs[1:]:
                    if inp.enabled:
                        parameter+=inp.variable_name + "=" + inp.code() + ", "

                if len(self.outputs) >= 2:
                    return {"code": f"""{self.inputs[0].code()}.{self.function_collection[self.search_value].identifier}({parameter})[{self.outputs.find(touched_socket.name)}]"""}
                else:
                    return {"code": f"""{self.inputs[0].code()}.{self.function_collection[self.search_value].identifier}({parameter})"""}

        else:
            self.add_error("No function selected", "You need to select a function")
            if touched_socket == self.inputs[0]:
                return {
                    "code": f"""
                            {self.outputs[0].code(7)}
                            """
                }

        return {"code": ""}