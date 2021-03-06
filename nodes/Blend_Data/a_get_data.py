import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode
from .a_get_data_pointers import get_known_types



class SN_GetDataFromIDNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_GetDataFromIDNode"
    bl_label = "Get Data"
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
        self.outputs.clear()
        self.no_data_error = False
        self.add_data_outputs(self.define_type)


    def update_data_type(self, context):
        identifiers = {"SN_StringSocket": ["STRING", "ENUM"], "SN_IntegerSocket": ["INT"], "SN_FloatSocket": ["FLOAT"], "SN_BooleanSocket": ["BOOLEAN"]}
        if not len(self.outputs) or not self.data_type in identifiers[self.outputs[0].bl_idname]:
            self.no_data_error = False
            self.outputs.clear()
            self.add_data_outputs(self.current_data_type)

        elif len(self.outputs) and self.outputs[0].bl_idname == "SN_StringSocket":
            if self.outputs[0].subtype == "ENUM" and self.data_type != "ENUM":
                self.no_data_error = False
                self.outputs.clear()
                self.add_data_outputs(self.current_data_type)
            elif self.outputs[0].subtype == "NONE" and self.data_type != "STRING":
                self.no_data_error = False
                self.outputs.clear()
                self.add_data_outputs(self.current_data_type)


    data_type: bpy.props.EnumProperty(items=[("STRING", "String", ""), ("INT", "Integer", ""), ("FLOAT", "Float", ""), ("BOOLEAN", "Boolean", ""), ("ENUM", "Enum", "")], name="Data Type", description="The data type you want to get", update=update_data_type)
    current_data_type: bpy.props.StringProperty(default="")
    collection_error: bpy.props.BoolProperty(default=False)
    no_data_error: bpy.props.BoolProperty(default=False)
    types: bpy.props.StringProperty(default="[]")
    categories: bpy.props.StringProperty(default="[]")
    category_enum: bpy.props.EnumProperty(items=get_cats, name="Category", update=update_cats)
    define_type: bpy.props.EnumProperty(items=get_types, name="Type", description="The type of the blend data you are trying to get from", update=update_type)


    def on_create(self,context):
        self.add_blend_data_input("Blend Data").mirror_name = True


    def add_data_outputs(self,data_identifier):
        try:
            for prop in eval(f"bpy.types.{data_identifier}.bl_rna.properties"):
                if prop.type == self.data_type:
                    out = self.add_output_from_prop(prop)
                    out.removable = True
        except:
            self.outputs.clear()
        if not len(self.outputs):
            self.no_data_error = True


    def update_outputs(self,socket):
        self.collection_error = False
        self.no_data_error = False
        if socket.subtype == "NONE":
            if socket.data_type == self.current_data_type and not len(self.outputs):
                self.add_data_outputs(socket.data_type)
            elif socket.data_type != self.current_data_type:
                self.outputs.clear()
                self.add_data_outputs(socket.data_type)

                self.types = "[]"
                self.categories = "[]"
                types = []
                if socket.data_type in get_known_types():
                    if type(get_known_types()[socket.data_type]) == dict:
                        cats = []
                        for cat in get_known_types()[socket.data_type]:
                            cats.append((cat, cat, ""))
                        self.categories = str(cats)
                        types = get_known_types()[socket.data_type][self.category_enum]
                    else:
                        types = get_known_types()[socket.data_type]

                else:
                    try:
                        for data_type in dir(bpy.types):
                            if eval("bpy.types." + socket.data_type) in eval("bpy.types." + data_type).__bases__:
                                name = eval("bpy.types." + data_type).bl_rna.name if eval("bpy.types." + data_type).bl_rna.name else data_type
                                types.append((data_type, name, eval("bpy.types." + data_type).bl_rna.description))
                    except:
                        types = []

                if types:
                    types.insert(0, (socket.data_type, socket.data_name, ""))
                    self.types = str(types)
                    self.define_type = socket.data_type

            self.current_data_type = socket.data_type
        else:
            self.types = "[]"
            self.categories = "[]"
            self.outputs.clear()
            self.current_data_type = ""
            self.collection_error = True


    def on_link_insert(self,link):
        if link.to_socket == self.inputs[0] and link.from_socket.bl_idname == "SN_BlendDataSocket":
            self.update_outputs(link.from_socket)

    def draw_node(self,context,layout):
        if self.categories != "[]":
            layout.prop(self, "category_enum", text="")
        if self.types != "[]":
            layout.prop(self, "define_type", text="")

        if self.current_data_type:
            layout.prop(self, "data_type", text="")
        if self.collection_error:
            layout.label(text="Connect single data block",icon="ERROR")
        elif self.no_data_error:
            layout.label(text="No data found",icon="ERROR")


    def code_evaluate(self, context, touched_socket):

        if self.inputs[0].links:
            if self.current_data_type == "Object" and self.define_type != "Object":
                return {
                    "code": f"{self.inputs[0].code()}.data.{touched_socket.variable_name}"
                }
            return {
                "code": f"{self.inputs[0].code()}.{touched_socket.variable_name}"
            }
        else:
            self.add_error("No blend data", "Blend data input is not connected", True)
            return {"code": "None"}