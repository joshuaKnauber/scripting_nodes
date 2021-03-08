import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode
from .a_get_data_pointers import get_known_types



class SN_GetDataCollectionNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_GetDataCollectionNode"
    bl_label = "Get Blend Data Collections"
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


    current_data_type: bpy.props.StringProperty(default="")
    no_data_error: bpy.props.BoolProperty(default=False)
    types: bpy.props.StringProperty(default="[]")
    categories: bpy.props.StringProperty(default="[]")
    category_enum: bpy.props.EnumProperty(items=get_cats, name="Category", update=update_cats)
    define_type: bpy.props.EnumProperty(items=get_types, name="Type", description="The type of the blend data you are trying to get from", update=update_type)


    def on_create(self,context):
        self.add_blend_data_input("Blend Data").mirror_name = True
        
        
    def add_data_outputs(self,data_type):
        try:
            for prop in eval(f"bpy.types.{data_type}.bl_rna.properties"):
                if prop.type == "COLLECTION":
                    if hasattr(prop, "fixed_type"):
                        out = self.add_blend_data_output(prop.name.replace("_", " ").title())
                        out.removable = True
                        out.subtype = "COLLECTION"
                        if hasattr(prop, "srna") and prop.srna:
                            out.data_type = prop.srna.identifier
                            out.data_name = prop.fixed_type.name
                            out.data_identifier = prop.identifier
                        else:
                            out.data_type = prop.fixed_type.identifier
                            out.data_name = prop.fixed_type.name
                            out.data_identifier = prop.identifier

        except:
            self.outputs.clear()
        if not len(self.outputs):
            self.no_data_error = True
        
        
    def update_outputs(self,socket):
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


    def on_link_insert(self,link):
        if link.to_socket == self.inputs[0] and link.from_socket.bl_idname == "SN_BlendDataSocket":
            self.update_outputs(link.from_socket)


    def draw_node(self,context,layout):
        if self.categories != "[]":
            layout.prop(self, "category_enum", text="")
        if self.types != "[]":
            layout.prop(self, "define_type", text="")

        elif self.no_data_error:
            layout.label(text="No data found",icon="ERROR")


    def code_evaluate(self, context, touched_socket):

        if self.inputs[0].links:
            if self.current_data_type == "Object" and self.define_type != "Object":
                return {
                    "code": f"{self.inputs[0].code()}.data.{touched_socket.data_identifier}"
                }
            return {
                "code": f"{self.inputs[0].code()}.{touched_socket.data_identifier}"
            }
        else:
            self.add_error("No blend data", "Blend data input is not connected", True)
            return {"code": "None"}