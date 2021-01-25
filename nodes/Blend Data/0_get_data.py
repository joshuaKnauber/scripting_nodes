import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode



class SN_GetDataFromIDNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_GetDataFromIDNode"
    bl_label = "Get Data"
    # bl_icon = "GRAPH"
    bl_width_default = 160
    
    node_options = {
        "default_color": (0.3,0.3,0.3),
    }

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


    def on_create(self,context):
        self.add_blend_data_input("Blend Data").mirror_name = True


    def add_data_outputs(self,data_identifier):
        try:
            for prop in eval(f"bpy.types.{data_identifier}.bl_rna.properties"):
                if prop.type == self.data_type:
                    out = self.add_output_from_prop(prop)
                    out.removable = True
            if not len(self.outputs):
                self.no_data_error = True
        except:
            self.outputs.clear()


    def update_outputs(self,socket):
        self.collection_error = False
        self.no_data_error = False
        if socket.subtype == "NONE":
            if socket.data_type == self.current_data_type and not len(self.outputs):
                self.add_data_outputs(socket.data_type)
            elif socket.data_type != self.current_data_type:
                self.outputs.clear()
                self.add_data_outputs(socket.data_type)
            self.current_data_type = socket.data_type
        else:
            self.outputs.clear()
            self.current_data_type = ""
            self.collection_error = True


    def on_link_insert(self,link):
        if link.to_socket == self.inputs[0]:
            self.update_outputs(link.from_socket)

    def on_copy(self, node):
        self.outputs.clear()
        self.collection_error = False
        self.current_data_type = ""
        self.no_data_error = False


    def draw_node(self,context,layout):
        if self.current_data_type:
            layout.prop(self, "data_type", text="")
        if self.collection_error:
            layout.label(text="Connect single data block",icon="ERROR")
        elif self.no_data_error:
            layout.label(text="No data found",icon="ERROR")


    def code_evaluate(self, context, touched_socket):
        if self.inputs[0].links:
            return {
                "code": f"{self.inputs[0].code()}.{touched_socket.variable_name}"
            }
        else:
            self.add_error("No blend data", "Blend data input is not connected", True)
            return {"code": "None"}