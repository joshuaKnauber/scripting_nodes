import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


def get_known_types():
    known_data_types = {
        "Object": [('Mesh', "Mesh", ""), ("Light", "Light", ""), ("Camera", "Camera", ""), ("GreasePencil", "GPencil", ""), ("Armature", "Armature", ""), ("BlendDataProbes", "Probe", ""), ("Speaker", "Speaker", ""), ("Curve", "Curve", ""), ("BlendDataFonts", "Font", ""), ("Volume", "Volume", ""), ("Lattice", "Lattice", "")],
        "Modifier": {"Object": [], "GPencil": [], "LineStyle": [], "FCurve": [], "Other": [('BrightContrastModifier', 'BrightContrastModifier', ''), ('ColorBalanceModifier', 'ColorBalanceModifier', ''), ('CurveModifier', 'Curve', ''), ('CurvesModifier', 'CurvesModifier', ''), ('HueCorrectModifier', 'HueCorrectModifier', ''), ('SequenceModifier', 'SequenceModifier', ''), ('SequencerTonemapModifierData', 'SequencerTonemapModifierData', ''), ('WhiteBalanceModifier', 'WhiteBalanceModifier', '')]},
        "Node": {"Compositor": [], "Shader": [], "Texture": []},
        "NodeSocket": [('NodeSocketBool', 'Boolean', ''), ('NodeSocketColor', 'Color', ''), ('NodeSocketFloat', 'Float', ''), ('NodeSocketImage', 'Image', ''), ('NodeSocketInt', 'Integer', ''), ('NodeSocketInterfaceImage', 'Image Interface', ''), ('NodeSocketInterfaceObject', 'Object Interface', ''), ('NodeSocketObject', 'Object', ''), ('NodeSocketShader', 'Shader', ''), ('NodeSocketString', 'String', ''), ('NodeSocketVector', 'Vector', '')],
        "NodeSocketInterface": [('NodeSocketBool', 'Boolean', ''), ('NodeSocketColor', 'Color', ''), ('NodeSocketFloat', 'Float', ''), ('NodeSocketImage', 'Image', ''), ('NodeSocketInt', 'Integer', ''), ('NodeSocketInterfaceImage', 'Image Interface', ''), ('NodeSocketInterfaceObject', 'Object Interface', ''), ('NodeSocketObject', 'Object', ''), ('NodeSocketShader', 'Shader', ''), ('NodeSocketString', 'String', ''), ('NodeSocketVector', 'Vector', '')],
    }
    used = ['BrightContrastModifier', 'ColorBalanceModifier', 'CurveModifier', 'CurvesModifier', 'HueCorrectModifier', 'SequenceModifier', 'SequencerTonemapModifierData', 'WhiteBalanceModifier']
    for class_type in dir(bpy.types):
        if "FModifier" in class_type and not class_type == "FModifier":
            known_data_types["Modifier"]["FCurve"].append((class_type, eval("bpy.types."+class_type+".bl_rna.name").replace(" Modifier", ""), ""))
        elif "Modifier" in class_type and not "Modifiers" in class_type and not class_type in ["GpencilModifier", "Modifier"]:
            if "gpencil" in class_type.lower():
                known_data_types["Modifier"]["GPencil"].append((class_type, eval("bpy.types."+class_type+".bl_rna.name").replace(" Modifier", ""), ""))
            elif "linestyle" in class_type.lower():
                known_data_types["Modifier"]["LineStyle"].append((class_type, eval("bpy.types."+class_type+".bl_rna.name").replace(" Modifier", ""), ""))
            else:
                if not class_type in used:
                    known_data_types["Modifier"]["Object"].append((class_type, eval("bpy.types."+class_type+".bl_rna.name").replace(" Modifier", ""), ""))
        elif "Node" in class_type and not "Tree" in class_type and not "Editor" in class_type and not "Socket" in class_type and not class_type in ["Node","Nodes","NodeCustomGroup","NodeFrame","NodeGroup","NodeGroupInput","NodeGroupOutput","NodeInputs","NodeInstanceHash","NodeInternal","NodeInternalSocketTemplate","NodeLink","NodeLinks","NodeOutputs","NodeReroute","NodeSocket","TextureNode","CompositorNode","ShaderNode"]:
            if "Compositor" in class_type:
                if class_type == "CompositorNodeOutputFileLayerSlots":
                    known_data_types["Node"]["Compositor"].append(("CompositorNodeOutputFileLayerSlots", "File Layer Output Slots", ""))
                else:
                    known_data_types["Node"]["Compositor"].append((class_type, eval("bpy.types." + class_type).bl_rna.name, eval("bpy.types." + class_type).bl_rna.description))
            elif "Shader" in class_type:
                known_data_types["Node"]["Shader"].append((class_type, eval("bpy.types." + class_type).bl_rna.name, eval("bpy.types." + class_type).bl_rna.description))
            elif "Texture" in class_type:
                known_data_types["Node"]["Texture"].append((class_type, eval("bpy.types." + class_type).bl_rna.name, eval("bpy.types." + class_type).bl_rna.description))

    return known_data_types


class SN_GetDataPointersNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_GetDataPointersNode"
    bl_label = "Get Blend Data"
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
    collection_error: bpy.props.BoolProperty(default=False)
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
                if prop.type == "POINTER":
                    if hasattr(prop, "identifier") and not prop.name == "RNA":
                        out = self.add_blend_data_output(prop.name.replace("_", " ").title())
                        out.removable = True
                        out.data_type = prop.fixed_type.identifier
                        out.data_name = prop.fixed_type.name
                        out.data_identifier = prop.identifier
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
            

    def on_copy(self, node):
        self.outputs.clear()
        self.collection_error = False
        self.current_data_type = ""
        self.no_data_error = False
        self.types = "[]"
        self.categories = "[]"

            
    def draw_node(self,context,layout):
        if self.categories != "[]":
            layout.prop(self, "category_enum", text="")
        if self.types != "[]":
            layout.prop(self, "define_type", text="")

        if self.collection_error:
            layout.label(text="Connect single data block",icon="ERROR")
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