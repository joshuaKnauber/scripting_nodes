import bpy
import json
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup
from ...interface.menu.rightclick import construct_from_property
from ...compiler.compiler import get_module
from ..Properties.property_util import get_data



class SN_OT_PasteOperator(bpy.types.Operator):
    bl_idname = "sn.paste_operator"
    bl_label = "Paste Operator"
    bl_description = "Pastes your copied operator in this node"
    bl_options = {"REGISTER","UNDO","INTERNAL"}
    
    node_name: bpy.props.StringProperty()
    
    def execute(self, context):
        if "bpy.ops." in context.window_manager.clipboard:
            context.space_data.node_tree.nodes[self.node_name].operator = context.window_manager.clipboard
        else:
            self.report({"WARNING"},message="Right-Click any button and click 'Copy Operator' to get a valid operator")
        return {"FINISHED"}
    
    
    
    
def create_sockets_from_operator(node, offset, index):
    props = node.addon_tree.sn_nodes["SN_OperatorNode"].items[node.custom_operator].node().properties

    # length is higher -> at least one socket got added
    if len(props) > len(node.inputs)-offset:
        if len(node.inputs) == offset:
            for prop in props:
                data = json.loads(construct_from_property("self",prop))["property"]
                inp = node.add_input_from_data(data)
                inp.disableable = True
        else:
            data = json.loads(construct_from_property("self",props[-1]))["property"]
            inp = node.add_input_from_data(data)
            inp.disableable = True
        
    # length is lower -> socket got removed
    elif len(props) < len(node.inputs)-offset:
        did_remove = False
        for i, prop in enumerate(props):
            if not node.inputs[i+offset].name == prop.name:
                node.inputs.remove(node.inputs[i+offset])
                did_remove = True
                break
        if not did_remove:
            node.inputs.remove(node.inputs[-1])
    
    # length is the same
    elif index >= 0:
        prop = props[index]
        inp = node.inputs[index+offset]
        node.inputs.remove(inp)
        data = json.loads(construct_from_property("self",prop))["property"]
        node.add_input_from_data(data).disableable = True
        node.inputs.move(len(node.inputs)-1,index+offset)




class SN_RunOperatorNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_RunOperatorNode"
    bl_label = "Run Operator"
    # bl_icon = "GRAPH"
    bl_width_default = 200

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
                for socket in self.inputs[2:]:
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
                inp = self.add_input_from_prop(prop,self.operator)
                if not prop.is_required:
                    inp.disableable = True
    
    
    def update_operator(self,context):
        if self.operator:
            self.add_inputs_from_internal()
        else:
            if "Call Invoke" in self.inputs: self.remove_input_range(2)
            else: self.remove_input_range(1)
        self.auto_compile()
            
            
    def update_inputs_from_operator(self, index=-1):
        if "Call Invoke" in self.inputs: create_sockets_from_operator(self, 2, index)
        else: create_sockets_from_operator(self, 1, index)

    
    def update_custom_operator(self,context):
        if "Call Invoke" in self.inputs: self.remove_input_range(2)
        else: self.remove_input_range(1)
        if self.custom_operator and self.custom_operator in self.addon_tree.sn_nodes["SN_OperatorNode"].items:
            self.update_inputs_from_operator()
        self.auto_compile()
    
    
    def update_use_internal(self,context):
        self.operator = ""
        self.custom_operator = ""
        self.auto_compile()
    
    
    op_name: bpy.props.StringProperty()
    operator: bpy.props.StringProperty(update=update_operator)
    use_internal: bpy.props.BoolProperty(name="Use Internal",
                                         description="Use blenders internal operators instead of your custom ones",
                                         update=update_use_internal)
    
    custom_operator: bpy.props.StringProperty(name="Custom Operator",
                                              description="Your custom operator",
                                              update=update_custom_operator)
    
    call_invoke: bpy.props.BoolProperty(name="Call Invoke",
                                        description="Calls the invoke function of the operator",
                                        default=True,
                                        update=SN_ScriptingBaseNode.auto_compile)


    def get_context_items(self,context):
        items = []
        areas = ["DEFAULT", "VIEW_3D", "IMAGE_EDITOR", "NODE_EDITOR", "SEQUENCE_EDITOR", "CLIP_EDITOR", "DOPESHEET_EDITOR",
                "DOPESHEET_ACTION_EDITOR", "DOPESHEET_SHAPEKEY_EDITOR", "DOPESHEET_GREASE_PENCIL", "DOPESHEET_MASK_EDITOR", "DOPESHEET_CACHE_FILE",
                "GRAPH_EDITOR", "NLA_EDITOR", "TEXT_EDITOR", "CONSOLE", "INFO", "TOPBAR", "STATUSBAR", "OUTLINER",
                "PROPERTIES", "FILE_BROWSER", "PREFERENCES"]
        for area in areas:
            items.append((area,area.replace("_"," ").title(),area.replace("_"," ").title()))
        return items


    context: bpy.props.EnumProperty(name="Operator Context",description="The context this operator should run in",
                                    items=get_context_items, update=SN_ScriptingBaseNode.auto_compile)
    
    
    def on_create(self,context):
        self.add_required_to_collection(["SN_OperatorNode"])
        self.add_boolean_input("Call Invoke").set_default(True)
        self.add_execute_input("Run Operator")
        self.add_execute_output("Execute").mirror_name = True
        
    def draw_node(self,context,layout):
        row = layout.row(align=True)
        if self.use_internal:
            if not self.operator:
                row.operator("sn.paste_operator",text="Paste Operator",icon="PASTEDOWN").node_name = self.name
            else:
                row.operator("sn.reset_property_node",icon="UNLINKED", text=self.op_name).node = self.name
            row.prop(self,"use_internal",text="",icon="BLENDER",invert_checkbox=True)
        elif "SN_OperatorNode" in self.addon_tree.sn_nodes:
            row.prop_search(self,"custom_operator",self.addon_tree.sn_nodes["SN_OperatorNode"],"items",text="",icon="VIEWZOOM")
            row.prop(self,"use_internal",text="",icon_value=bpy.context.scene.sn_icons[ "serpens" ].icon_id)

        row = layout.row()
        row.scale_y = 1.2
        row.enabled = get_module(self.addon_tree) != None
        op = row.operator("sn.test_function",text="Run Operator",icon="PLAY")
        op.node = self.name

        layout.prop(self,"context",text="Context")

        if not "Call Invoke" in self.inputs:
            layout.prop(self,"call_invoke")


    def code_evaluate(self, context, touched_socket):
        operator = ""

        context_modes = {
            "DOPESHEET_ACTION_EDITOR": "ACTION",
            "DOPESHEET_SHAPEKEY_EDITOR": "SHAPEKEY",
            "DOPESHEET_GREASE_PENCIL": "GPENCIL",
            "DOPESHEET_MASK_EDITOR": "MASK",
            "DOPESHEET_CACHE_FILE": "CACHEFILE"
        }

        set_context_mode = ""
        set_context = ""
        if self.context != "DEFAULT":
            set_context = f"bpy.context.area.type = '{self.context}'"
            if self.context in context_modes:
                set_context_mode = f"bpy.context.space_data.mode = '{context_modes[self.context]}'"
                set_context = "bpy.context.area.type = 'DOPESHEET_EDITOR'"
        
        if self.use_internal:
            if self.operator:
                operator = self.operator.split("(")[0] + "("
                
                if "Call Invoke" in self.inputs:
                    operator += f"'INVOKE_DEFAULT' if {self.inputs['Call Invoke'].code()} else 'EXEC_DEFAULT',"
                else:
                    if self.call_invoke:
                        operator += "\"INVOKE_DEFAULT\","
                    else:
                        operator += "\"EXEC_DEFAULT\","
            else:
                self.add_error("No Operator", "No operator selected")

        else:
            if self.custom_operator and self.custom_operator in self.addon_tree.sn_nodes["SN_OperatorNode"].items:
                item = self.addon_tree.sn_nodes["SN_OperatorNode"].items[self.custom_operator]
                operator = "bpy.ops.sna." + item.identifier + "("

                if "Call Invoke" in self.inputs:
                    operator += f"'INVOKE_DEFAULT' if {self.inputs['Call Invoke'].code()} else 'EXEC_DEFAULT',"
                else:
                    if self.call_invoke:
                        operator += "\"INVOKE_DEFAULT\","
                    else:
                        operator += "\"EXEC_DEFAULT\","
            else:
                self.add_error("No Operator", "No operator selected")

        if operator:
            for inp in self.inputs:
                if inp.group == "DATA" and inp.enabled and not inp.name =="Call Invoke":
                    operator += f"{inp.variable_name}={inp.code()},"

            operator += ")"

        return {
            "code": f"""
                    {"op_reset_context = bpy.context.area.type" if set_context else ""}
                    {set_context}
                    {set_context_mode}
                    {operator}
                    {"bpy.context.area.type = op_reset_context" if set_context else ""}
                    {self.outputs[0].code(5)}
                    """
        }