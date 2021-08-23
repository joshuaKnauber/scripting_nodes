import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode
from ..Program.run_operator import create_sockets_from_operator
from ..Properties.property_util import get_data


class SN_ButtonNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_ButtonNode"
    bl_label = "Button"
    # bl_icon = "GRAPH"
    bl_width_default = 160
    
    node_options = {
        "default_color": (0.3,0.3,0.3),
    }

    def find_op_node(self):
        for graph in self.addon_tree.sn_graphs:
            for node in graph.node_tree.nodes:
                if node.bl_idname == "SN_OperatorNode" and node.operator_name == self.custom_operator:
                    return node

    def on_outside_update(self, string_data=""):
        if "NAMECHANGE" in string_data:
            if string_data.split("NAMECHANGE")[0] == self.custom_operator:
                self["custom_operator"] = string_data.split("NAMECHANGE")[1]
            return
        if self.custom_operator and self.custom_operator in self.addon_tree.sn_nodes["SN_OperatorNode"].items:
            new_data = get_data(string_data)
            if new_data["group_path"] == "self" and self.find_op_node().uid == new_data["property"]["created_from"]:
                for socket in self.inputs[5:]:
                    if socket.variable_name == new_data["property"]["identifier"] and socket.default_text != new_data["property"]["name"]:
                        socket.default_text = new_data["property"]["name"]
                    elif socket.default_text == new_data["property"]["name"] and socket.variable_name != new_data["property"]["identifier"]:
                        socket.variable_name = new_data["property"]["identifier"]
                    elif socket.variable_name == new_data["property"]["identifier"] and socket.default_text == new_data["property"]["name"]:
                        if socket.bl_idname != self.prop_types[new_data["property"]["type"]]:
                            enabled = socket.enabled
                            socket = self.change_socket_type(socket, self.prop_types[new_data["property"]["type"]])
                            socket.disableable = True
                            socket.enabled = enabled

                        if socket.subtype != self.subtype_from_prop_subtype(new_data["property"]["type"],new_data["property"]["subtype"],new_data["property"]["size"]):
                            socket.subtype = self.subtype_from_prop_subtype(new_data["property"]["type"],new_data["property"]["subtype"],new_data["property"]["size"])

                        if new_data["property"]["type"] == "ENUM":
                            socket.enum_values = new_data["property"]["items"]


    def add_inputs_from_internal(self):
        rna = eval(self.operator.split("(")[0] + ".get_rna_type()")
        name = eval(self.operator.split("(")[0] + ".idname_py()").split(".")[-1]
        self.op_name = rna.name if rna.name else name.replace("_", " ").title()
        for prop in rna.properties:
            if not prop.name == "RNA":
                self.add_input_from_prop(prop,self.operator).disableable = True
    
    
    def update_operator(self,context):
        if self.operator:
            self.add_inputs_from_internal()
        else:
            self.remove_input_range(5)
        self.auto_compile()


    def update_inputs_from_operator(self, index=-1):
        create_sockets_from_operator(self,5,index)


    def update_custom_operator(self,context):
        self.remove_input_range(5)
        if self.custom_operator and self.custom_operator in self.addon_tree.sn_nodes["SN_OperatorNode"].items:
            self.update_inputs_from_operator()
        self.auto_compile()
    
    
    def update_use_internal(self,context):
        self.operator = ""
        self.custom_operator = ""
        self.auto_compile()
    
    
    operator: bpy.props.StringProperty(update=update_operator)
    op_name: bpy.props.StringProperty()
    use_internal: bpy.props.BoolProperty(name="Use Internal",
                                         description="Use blenders internal operators instead of your custom ones",
                                         update=update_use_internal)
    
    custom_operator: bpy.props.StringProperty(name="Custom Operator",
                                              description="Your custom operator",
                                              update=update_custom_operator)
    
    
    def draw_node(self,context,layout):
        row = layout.row(align=True)
        if self.use_internal:
            if not self.operator:
                row.operator("sn.paste_operator",text="Paste Operator",icon="PASTEDOWN").node_name = self.name
            else:
                op = row.operator("sn.reset_property_node",icon="UNLINKED", text=self.op_name)
                op.node = self.name
            row.prop(self,"use_internal",text="",icon="BLENDER",invert_checkbox=True)
        elif "SN_OperatorNode" in self.addon_tree.sn_nodes:
            row.prop_search(self,"custom_operator",self.addon_tree.sn_nodes["SN_OperatorNode"],"items",text="",icon="VIEWZOOM")
            row.prop(self,"use_internal",text="",icon_value=bpy.context.scene.sn_icons[ "serpens" ].icon_id)


    def on_create(self,context):
        self.add_required_to_collection(["SN_OperatorNode"])
        self.add_interface_input("Interface").mirror_name = True

        self.add_string_input("Label").set_default("New Button")
        self.add_boolean_input("Emboss").set_default(True)
        self.add_boolean_input("Depress").set_default(False)
        self.add_icon_input("Icon")
    

    def code_evaluate(self, context, touched_socket):

        layout = touched_socket.links[0].from_node.what_layout(touched_socket.links[0].from_socket)
        text = self.inputs['Label'].code()
        emboss = self.inputs['Emboss'].code()
        depress = self.inputs['Depress'].code()
        icon = self.inputs['Icon'].code()
        
        operator = ""
        if self.use_internal:
            if self.operator:
                operator = self.operator.split("(")[0].replace("bpy.ops.","")
        elif self.custom_operator and self.custom_operator in self.addon_tree.sn_nodes["SN_OperatorNode"].items:
            item = self.addon_tree.sn_nodes["SN_OperatorNode"].items[self.custom_operator]
            operator = "sna." + item.identifier

        if operator:
            props = []
            for i,inp in enumerate(self.inputs):
                if i > 4 and inp.enabled:
                    props.append("op." + inp.variable_name + " = " + inp.code() + "\n")
                    
        else:
            self.add_error("No Operator", "No operator selected")
            return {"code":""}
        
        return {
            "code": f"""
                    op = {layout}.operator("{operator}",text={text},emboss={emboss},depress={depress},icon_value={icon})
                    {self.list_code(props,5)}
                    """
        }