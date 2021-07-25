import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup
from ..Program.run_operator import create_sockets_from_operator


def sn_append_interface(self, context):
    row = self.layout.row()
    row.alert = True
    op = row.operator("sn.select_interface_add",text="Select",icon="CHECKMARK")
    op.idname = self.bl_idname
    
    
    
remove_interfaces = []
picker_node = None


space_names = {
            "EMPTY": "Window",
            "VIEW_3D": "3D View",
            "IMAGE_EDITOR": "Image",
            "NODE_EDITOR": "Node Editor",
            "SEQUENCE_EDITOR": "Sequencer",
            "CLIP_EDITOR": "Clip",
            "DOPESHEET_EDITOR": "Dopesheet",
            "GRAPH_EDITOR": "Graph Editor",
            "NLA_EDITOR": "NLA Editor",
            "TEXT_EDITOR": "Text",
            "CONSOLE": "Console",
            "INFO": "Info",
            "OUTLINER": "Outliner",
            "PROPERTIES": "Property Editor",
            "FILE_BROWSER": "File Browser"
        }



class SN_AddKeymapDisplay(bpy.types.Operator):
    bl_idname = "sn.add_keymap_display"
    bl_label = "Add Display"
    bl_description = "Adds the keymap display node"
    bl_options = {"REGISTER","UNDO","INTERNAL"}

    keymap: bpy.props.StringProperty(options={"HIDDEN"})
    item: bpy.props.StringProperty(options={"HIDDEN"})

    def execute(self, context):
        bpy.ops.node.add_node("INVOKE_DEFAULT",type="SN_DisplayKeymapItem",use_transform=True)
        node = context.space_data.node_tree.nodes.active
        node.item = self.item
        node.keymap = self.keymap
        return {"FINISHED"}
    
    

class SN_OT_SelectInterfaceAdd(bpy.types.Operator):
    bl_idname = "sn.select_interface_add"
    bl_label = "Select"
    bl_description = "Select this element in the interface"
    bl_options = {"REGISTER","UNDO","INTERNAL"}
    
    idname: bpy.props.StringProperty(options={"HIDDEN"})
    
    def remove_registered_interfaces(self):
        global remove_interfaces
        for interface in remove_interfaces:
            try:
                interface.remove(sn_append_interface)
            except:
                pass
        remove_interfaces.clear()

    def execute(self, context):
        global picker_node
        if picker_node:
            picker_node.picked = self.idname
        picker_node = None
        self.remove_registered_interfaces()
        for area in context.screen.areas:
            area.tag_redraw()
        return {"FINISHED"}


    

class SN_OT_StartInterfacePicker(bpy.types.Operator):
    bl_idname = "sn.pick_interface"
    bl_label = "Select"
    bl_description = "Select an element in the interface"
    bl_options = {"REGISTER","UNDO","INTERNAL"}
    
    node: bpy.props.StringProperty()
    selection: bpy.props.EnumProperty(items=[("ALL","ALL","ALL"),
                                             ("PANELS","PANELS","PANELS"),
                                             ("MENUS","MENUS","MENUS")],
                                      options={"SKIP_SAVE"})
    
    @classmethod
    def poll(cls, context):
        global remove_interfaces
        return len(remove_interfaces) == 0
    
    def get_interfaces(self):
        interfaces = []
        for name in dir(bpy.types):
            try:
                interface = eval("bpy.types."+name)
                if self.selection != "PANELS":
                    if hasattr(interface.bl_rna.base,"identifier") and interface.bl_rna.base.identifier == "Menu":
                        interfaces.append(name)
                if self.selection != "MENUS":
                    if hasattr(interface.bl_rna.base,"identifier") and interface.bl_rna.base.identifier == "Panel":
                        interfaces.append(name)
            except:
                pass
        return interfaces

    def execute(self, context):
        global picker_node
        global remove_interfaces
        picker_node = context.space_data.node_tree.nodes[self.node]
        for interface in self.get_interfaces():
            try:
                eval("bpy.types."+interface+".append(sn_append_interface)")
                remove_interfaces.append(eval("bpy.types."+interface))
            except:
                pass
        for area in context.screen.areas:
            area.tag_redraw()
        return {"FINISHED"}




class SN_OT_RecordKey(bpy.types.Operator):
    bl_idname = "sn.record_key"
    bl_label = "Record Key"
    bl_description = "Records the next pressed key"
    bl_options = {"REGISTER","UNDO","INTERNAL"}
    
    node: bpy.props.StringProperty()

    def invoke(self, context, event):
        context.space_data.node_tree.nodes[self.node].recording = True
        context.window_manager.modal_handler_add(self)
        return {"RUNNING_MODAL"}
    
    def assign_key(self,context,key_type):
        if hasattr(context,"space_data") and context.space_data:
            if hasattr(context.space_data,"node_tree"):
                node = context.space_data.node_tree.nodes[self.node]
                node.key = key_type
                node.recording = False
                context.area.tag_redraw()

    def modal(self, context, event):
        
        invalid = ["MOUSEMOVE","INBETWEEN_MOUSEMOVE","TRACKPADPAN","TRACKPADZOOM","MOUSEROTATE","MOUSESMARTZOOM",
                   "TEXTINPUT","WINDOW_DEACTIVATE","ACTIONZONE_AREA","ACTIONZONE_REGION","ACTIONZONE_FULLSCREEN"]
        
        if not event.type in invalid and not "TIMER" in event.type and not "NDOF" in event.type:
            self.assign_key(context,event.type)
            return {"FINISHED"}
        return {"RUNNING_MODAL"}
        




class SN_OnKeypressNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_OnKeypressNode"
    bl_label = "On Keypress"
    # bl_icon = "GRAPH"
    bl_width_default = 200

    node_options = {
        "default_color": (0.2,0.2,0.2),
        "starts_tree": True,
        "imperative_once": True,
        "unregister_once": True
    }
    
    
    def get_spaces(self,context):
        items = [("EMPTY","Any Space","Run this shortcut in any space")]
        spaces = ["VIEW_3D", "IMAGE_EDITOR", "NODE_EDITOR", "SEQUENCE_EDITOR","CLIP_EDITOR",
                  "DOPESHEET_EDITOR", "GRAPH_EDITOR", "NLA_EDITOR", "TEXT_EDITOR","CONSOLE",
                  "INFO", "OUTLINER", "PROPERTIES","FILE_BROWSER"]
        for item in spaces:
            items.append((item,item.replace("_"," ").title(),item.replace("_"," ").title()))
        return items
    
    def update_use_internal(self,context):
        self.panel = ""
        self.menu = ""
        self.pie = ""
        self.operator = ""
        self.custom_operator = ""
        self.auto_compile()
        
    def update_picked(self,context):
        if self.picked:
            elem = eval("bpy.types."+self.picked)
            if elem.bl_rna.base.identifier == "Menu":
                if "pie" in self.picked.lower():
                    self.action = "PIE_MENU"
                    self.pie = self.picked
                else:
                    self.action = "MENU"
                    self.menu = self.picked
            elif elem.bl_rna.base.identifier == "Panel":
                self.action = "PANEL"
                self.panel = self.picked
            self.picked = ""
            
    
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
            self.remove_input_range(0)
        self.auto_compile()
            
            
    def update_inputs_from_operator(self, index=-1):
        create_sockets_from_operator(self,0,index)

    
    def update_custom_operator(self,context):
        self.remove_input_range(0)
        if self.custom_operator and self.custom_operator in self.addon_tree.sn_nodes["SN_OperatorNode"].items:
            self.update_inputs_from_operator()
        self.auto_compile()
    
    
    key: bpy.props.StringProperty(name="Key",default="Y", update=SN_ScriptingBaseNode.auto_compile)

    recording: bpy.props.BoolProperty(name="Recording",default=False)

    ctrl: bpy.props.BoolProperty(name="Ctrl",
                                  description="If the ctrl key has to be pressed",
                                  default=False,
                                  update=SN_ScriptingBaseNode.auto_compile)
    
    alt: bpy.props.BoolProperty(name="Alt",
                                  description="If the alt key has to be pressed",
                                  default=False,
                                  update=SN_ScriptingBaseNode.auto_compile)
    
    shift: bpy.props.BoolProperty(name="Shift",
                                  description="If the shift key has to be pressed",
                                  default=False,
                                  update=SN_ScriptingBaseNode.auto_compile)
    
    value: bpy.props.EnumProperty(name="Value",
                                  description="The way the key has to be pressed",
                                  items=[("PRESS","On Press","The action is run when the key is pressed once"),
                                         ("RELEASE","On Release","The action is run when the key is released"),
                                         ("CLICK","On Click","The action is run when the mouse button is clicked once"),
                                         ("DOUBLE_CLICK","On Double Click","The action is run when the mouse button is clicked twice"),
                                         ("ANY","Any","The action will run with any of the above ways")],
                                  update=SN_ScriptingBaseNode.auto_compile)
    
    repeat: bpy.props.BoolProperty(name="Repeat Key",
                                   description="Repeat the action when the key is held down",
                                   default=False,
                                   update=SN_ScriptingBaseNode.auto_compile)
    
    space: bpy.props.EnumProperty(name="Space",
                                  description="The space where this shortcut is active",
                                  items=get_spaces,
                                  update=SN_ScriptingBaseNode.auto_compile)
    
    
    action: bpy.props.EnumProperty(name="Action",
                                   description="The type of action to be performed",
                                   update=update_use_internal,
                                   items=[("OPERATOR","Operator","Run an operator when the key is pressed"),
                                          ("PANEL","Panel","Open a panel when the key is pressed"),
                                          ("MENU","Menu","Open a menu when the key is pressed"),
                                          ("PIE_MENU","Pie","Open a pie menu when the key is pressed")])
    
    keep_open: bpy.props.BoolProperty(name="Keep Open",
                                      description="Keep the panel open after a property is changed",
                                      default=True,
                                      update=SN_ScriptingBaseNode.auto_compile)
    
    use_internal: bpy.props.BoolProperty(name="Use Internal",
                                         description="Uses the internal ones from blender instead of your custom ones",
                                         default=False,
                                         update=update_use_internal)
    
    panel: bpy.props.StringProperty(name="Panel",
                                    description="The panel to open when the key is pressed",
                                    update=SN_ScriptingBaseNode.auto_compile)
    
    menu: bpy.props.StringProperty(name="Menu",
                                    description="The menu to open when the key is pressed",
                                    update=SN_ScriptingBaseNode.auto_compile)
    
    pie: bpy.props.StringProperty(name="Pie Menu",
                                    description="The pie menu to open when the key is pressed",
                                    update=SN_ScriptingBaseNode.auto_compile)
    
    picked: bpy.props.StringProperty(update=update_picked)    
    
    op_name: bpy.props.StringProperty()
    operator: bpy.props.StringProperty(update=update_operator)
    
    custom_operator: bpy.props.StringProperty(name="Custom Operator",
                                              description="Your custom operator",
                                              update=update_custom_operator)
    

    def draw_node(self,context,layout):
        row = layout.row(align=True)
        row.prop(self,"space",text="")
        row.prop(self,"value",text="")
        op = row.operator("sn.add_keymap_display",text="",icon="FORWARD")
        op.keymap = space_names[self.space]
        op.item = self.code_evaluate(context, None, get_action=True)
        
        layout.operator("sn.record_key",text=self.key,depress=self.recording).node = self.name
        row = layout.row(align=True)
        row.prop(self,"ctrl",toggle=True)
        row.prop(self,"shift",toggle=True)
        row.prop(self,"alt",toggle=True)
        layout.prop(self,"repeat")
        layout.separator()

        row = layout.row(align=True)
        row.prop(self,"action",text="")
        if self.use_internal:
            row.prop(self,"use_internal",text="",icon="BLENDER",invert_checkbox=True)
        else:
            row.prop(self,"use_internal",text="",icon_value=bpy.context.scene.sn_icons[ "serpens" ].icon_id)

        if self.action == "PANEL":
            if self.use_internal:
                name = self.panel.replace("_"," ").title() if self.panel else "Select Panel"
                op = layout.operator("sn.pick_interface",text=name,icon="EYEDROPPER")
                op.node = self.name
                op.selection = "PANELS"
            elif "SN_PanelNode" in self.addon_tree.sn_nodes:
                layout.prop_search(self,"panel",self.addon_tree.sn_nodes["SN_PanelNode"],"items",text="",icon="VIEWZOOM")
                layout.prop(self,"keep_open")

        elif self.action == "MENU":
            if self.use_internal:
                name = self.menu.replace("_"," ").title() if self.menu else "Select Menu"
                op = layout.operator("sn.pick_interface",text=name,icon="EYEDROPPER")
                op.node = self.name
                op.selection = "MENUS"
            elif "SN_MenuNode" in self.addon_tree.sn_nodes:
                layout.prop_search(self,"menu",self.addon_tree.sn_nodes["SN_MenuNode"],"items",text="",icon="VIEWZOOM")

        elif self.action == "PIE_MENU":
            if self.use_internal:
                name = self.pie.replace("_"," ").title() if self.pie else "Select Pie Menu"
                op = layout.operator("sn.pick_interface",text=name,icon="EYEDROPPER")
                op.node = self.name
                op.selection = "MENUS"
            elif "SN_PieMenuNode" in self.addon_tree.sn_nodes:
                layout.prop_search(self,"pie",self.addon_tree.sn_nodes["SN_PieMenuNode"],"items",text="",icon="VIEWZOOM")
                
        elif self.action == "OPERATOR":
            if self.use_internal:
                if not self.operator:
                    layout.operator("sn.paste_operator",text="Paste Operator",icon="PASTEDOWN").node_name = self.name
                else:
                    layout.operator("sn.reset_property_node",icon="UNLINKED", text=self.op_name).node = self.name
            elif "SN_OperatorNode" in self.addon_tree.sn_nodes:
                layout.prop_search(self,"custom_operator",self.addon_tree.sn_nodes["SN_OperatorNode"],"items",text="",icon="VIEWZOOM")


    def on_create(self,context):
        self.add_required_to_collection(["SN_PanelNode","SN_MenuNode","SN_PieMenuNode","SN_OperatorNode"])


    def code_imperative(self, context):
        return {
            "code": f"""
                    addon_keymaps = []
                    """
        }
        
        
    def code_evaluate(self, context, touched_socket, get_action=False):
        
        global space_names
        
        properties = []

        if self.action == "PANEL":
            action = "wm.call_panel"
            panel = "RENDER_PT_dimensions"
            if self.use_internal:
                if self.panel: panel = self.panel
            elif self.panel in self.addon_tree.sn_nodes["SN_PanelNode"].items:
                panel = self.addon_tree.sn_nodes["SN_PanelNode"].items[self.panel].node().idname()
            properties.append(f"kmi.properties.name = \"{panel}\"\n")
            properties.append(f"kmi.properties.keep_open = {self.keep_open}\n")

        elif self.action == "MENU":
            action = "wm.call_menu"
            menu = "VIEW3D_MT_add"
            if self.use_internal:
                if self.menu: menu = self.menu
            elif self.menu in self.addon_tree.sn_nodes["SN_MenuNode"].items:
                menu = self.addon_tree.sn_nodes["SN_MenuNode"].items[self.menu].node().idname()
            properties.append(f"kmi.properties.name = \"{menu}\"\n")

        elif self.action == "PIE_MENU":
            action = "wm.call_menu_pie"
            pie = "VIEW3D_MT_shading_pie"
            if self.use_internal:
                if self.pie: pie = self.pie
            elif self.pie in self.addon_tree.sn_nodes["SN_PieMenuNode"].items:
                pie = self.addon_tree.sn_nodes["SN_PieMenuNode"].items[self.pie].node().idname()
            properties.append(f"kmi.properties.name = \"{pie}\"\n")
            
        elif self.action == "OPERATOR":
            action = "mesh.primitive_monkey_add"
            if self.use_internal:
                if self.operator:
                    action = self.operator.split("(")[0].replace("bpy.ops.","")
            else:
                if self.custom_operator and self.custom_operator in self.addon_tree.sn_nodes["SN_OperatorNode"].items:
                    item = self.addon_tree.sn_nodes["SN_OperatorNode"].items[self.custom_operator]
                    action = "sna." + item.identifier
            for inp in self.inputs:
                if inp.enabled:
                    properties.append(f"kmi.properties.{inp.variable_name} = {inp.code()}\n")
            
        if get_action:
            return action
        
        return {
            "code": f"""
                    def register_key_{self.uid}():
                        kc = bpy.context.window_manager.keyconfigs.addon
                        if kc:
                            km = kc.keymaps.new(name="{space_names[self.space]}", space_type="{self.space}")
                            kmi = km.keymap_items.new("{action}",
                                                        type= "{self.key}",
                                                        value= "{self.value}",
                                                        repeat= {self.repeat},
                                                        ctrl={self.ctrl},
                                                        alt={self.alt},
                                                        shift={self.shift})
                            {self.list_code(properties,7)}
                            addon_keymaps.append((km, kmi))
                    """

        }

    
    def code_register(self, context):
        return {
            "code": f"""
                    register_key_{self.uid}()
                    """
        }


    def code_unregister(self, context):
        return {
            "code": f"""
                    for km,kmi in addon_keymaps:
                        km.keymap_items.remove(kmi)
                    addon_keymaps.clear()
                    """
        }