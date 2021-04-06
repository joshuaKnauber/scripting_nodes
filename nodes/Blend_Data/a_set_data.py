import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode
from .a_get_data_pointers import get_known_types



class SN_SetDataNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_SetDataNode"
    bl_label = "Set Data"
    # bl_icon = "GRAPH"
    bl_width_default = 160
    
    node_options = {
        "default_color": (0.3,0.3,0.3),
    }

    def get_cats(self, context):
        return eval(self.categories)

    def update_cats(self, context):
        types = get_known_types()[self.current_data_type][self.category_enum]
        types.insert(0, (self.current_data_type, self.current_data_type, ""))
        self.types = str(types)
        self.define_type = self.current_data_type

    def get_types(self, context):
        return eval(self.types)

    def update_type(self, context):
        self.remove_input_range(2)
        self.no_data_error = False
        self.add_data_inputs(self.define_type)

    def update_data_type(self, context):
        identifiers = {"SN_StringSocket": ["STRING", "ENUM"], "SN_IntegerSocket": ["INT"], "SN_FloatSocket": ["FLOAT"], "SN_BooleanSocket": ["BOOLEAN"]}
        if not len(self.inputs)-2 or not self.data_type in identifiers[self.inputs[2].bl_idname]:
            self.no_data_error = False
            self.remove_input_range(2)
            self.add_data_inputs(self.current_data_type)

        elif len(self.inputs)-2 and self.inputs[2].bl_idname == "SN_StringSocket":
            if self.inputs[2].subtype == "ENUM" and self.data_type != "ENUM":
                self.no_data_error = False
                self.remove_input_range(2)
                self.add_data_inputs(self.current_data_type)
            elif self.inputs[2].subtype == "NONE" and self.data_type != "STRING":
                self.no_data_error = False
                self.remove_input_range(2)
                self.add_data_inputs(self.current_data_type)


    data_type: bpy.props.EnumProperty(items=[("STRING", "String", ""), ("INT", "Integer", ""), ("FLOAT", "Float", ""), ("BOOLEAN", "Boolean", ""), ("ENUM", "Enum", "")], name="Data Type", description="The data type you want to get", update=update_data_type)
    current_data_type: bpy.props.StringProperty(default="")
    no_data_error: bpy.props.BoolProperty(default=False)
    types: bpy.props.StringProperty(default="[]")
    categories: bpy.props.StringProperty(default="[]")
    category_enum: bpy.props.EnumProperty(items=get_cats, name="Category", update=update_cats)
    define_type: bpy.props.EnumProperty(items=get_types, name="Type", description="The type of the blend data you are trying to get from", update=update_type)


    def on_create(self,context):
        self.add_execute_input("Set Data")
        self.add_blend_data_input("Blend Data").mirror_name = True
        self.add_execute_output("Execute").mirror_name = True
        
        
    def add_data_inputs(self,data_type):
        try:
            for prop in eval(f"bpy.types.{data_type}.bl_rna.properties"):
                if not prop.is_readonly and prop.type == self.data_type:
                    inp = self.add_input_from_prop(prop)
                    inp.removable = True
        except:
            self.remove_input_range(2)
        if not len(self.inputs)-2:
            self.no_data_error = True


    def update_inputs(self,socket):
        self.inputs[1].subtype = socket.subtype
        self.no_data_error = False
        data_type = socket.data_type_collection if socket.data_type_collection else socket.data_type
        if data_type == self.current_data_type and not len(self.inputs)-2:
            self.add_data_inputs(data_type)
        elif data_type != self.current_data_type and data_type != "":
            self.remove_input_range(2)
            self.add_data_inputs(data_type)

            self.types = "[]"
            self.categories = "[]"
            types = []
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

        if data_type != "":
            self.current_data_type = data_type


    def on_link_insert(self,link):
        if link.to_socket == self.inputs[1] and link.from_socket.bl_idname == "SN_BlendDataSocket":
            self.update_inputs(link.from_socket)


    def draw_node(self,context,layout):
        if self.categories != "[]":
            layout.prop(self, "category_enum", text="")
        if self.types != "[]":
            layout.prop(self, "define_type", text="")

        if self.current_data_type:
            layout.prop(self, "data_type", text="")

        elif self.no_data_error:
            layout.label(text="No data found",icon="ERROR")


    def code_evaluate(self, context, touched_socket):

        set_data = []
        if self.inputs[1].links:
            for inp in self.inputs[2:]:
                if self.current_data_type == "Object" and self.define_type != "Object":
                    set_data.append(self.inputs[1].code() + ".data." + inp.variable_name + "=" + inp.code() + "\n")
                else:
                    set_data.append(self.inputs[1].code() + "." + inp.variable_name + "=" + inp.code() + "\n")
        else:
            self.add_error("No blend data", "Blend data input is not connected", True)

        return {
            "code": f"""
                    {self.list_code(set_data, 5)}
                    {self.outputs[0].code(5)}
            """
        }