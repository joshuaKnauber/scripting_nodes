import bpy
from ..base_node import SN_ScriptingBaseNode
from ..Program.Run_Operator import on_operator_ref_update



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



class SN_OnKeypressNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_OnKeypressNode"
    bl_label = "On Keypress"
    is_trigger = True
    bl_width_default = 200
    
    key: bpy.props.StringProperty(name="Key",default="Y", update=SN_ScriptingBaseNode._evaluate)

    recording: bpy.props.BoolProperty(name="Recording",default=False)

    ctrl: bpy.props.BoolProperty(name="Ctrl",
                                  description="If the ctrl key has to be pressed",
                                  default=False,
                                  update=SN_ScriptingBaseNode._evaluate)
    
    alt: bpy.props.BoolProperty(name="Alt",
                                  description="If the alt key has to be pressed",
                                  default=False,
                                  update=SN_ScriptingBaseNode._evaluate)
    
    shift: bpy.props.BoolProperty(name="Shift",
                                  description="If the shift key has to be pressed",
                                  default=False,
                                  update=SN_ScriptingBaseNode._evaluate)
    
    value: bpy.props.EnumProperty(name="Value",
                                  description="The way the key has to be pressed",
                                  items=[("PRESS","On Press","The action is run when the key is pressed once"),
                                         ("RELEASE","On Release","The action is run when the key is released"),
                                         ("CLICK","On Click","The action is run when the mouse button is clicked once"),
                                         ("DOUBLE_CLICK","On Double Click","The action is run when the mouse button is clicked twice"),
                                         ("ANY","Any","The action will run with any of the above ways"),
                                         ("CLICK_DRAG","On Click Drag","The action is run when you click and drag")],
                                  update=SN_ScriptingBaseNode._evaluate)
    
    direction: bpy.props.EnumProperty(name="Direction",
                                  description="Direction to drag the mouse in to run the action",
                                  items=[("ANY","Any Direction","The action will run when you click and drag in any direction"),
                                         ("NORTH","North","The action will run when you click and drag in this direction"),
                                         ("NORTH_EAST","North East","The action will run when you click and drag in this direction"),
                                         ("EAST","East","The action will run when you click and drag in this direction"),
                                         ("SOUTH_EAST","South East","The action will run when you click and drag in this direction"),
                                         ("SOUTH","South","The action will run when you click and drag in this direction"),
                                         ("SOUT_WEST","South West","The action will run when you click and drag in this direction"),
                                         ("WEST","West","The action will run when you click and drag in this direction"),
                                         ("NORTH_WEST","North West","The action will run when you click and drag in this direction")],
                                  update=SN_ScriptingBaseNode._evaluate)
    
    repeat: bpy.props.BoolProperty(name="Repeat Key",
                                   description="Repeat the action when the key is held down",
                                   default=False,
                                   update=SN_ScriptingBaseNode._evaluate)
    
    def on_create(self, context):
        self.ref_ntree = self.node_tree
        self.order = 3
    
    def reset_inputs(self, context=None):
        self.inputs.clear()
        self.pasted_operator = ""
        self.ref_SN_OperatorNode = ""
        self._evaluate(context)
    
    def get_spaces(self, context):
        items = [("EMPTY","Any Space","Run this shortcut in any space")]
        for item in list(space_names.keys())[1:]:
            items.append((item,item.replace("_"," ").title(),item.replace("_"," ").title()))
        return items
    
    space: bpy.props.EnumProperty(items=get_spaces,
                                name="Space",
                                description="The space which this action should be able to run in",
                                update=SN_ScriptingBaseNode._evaluate)

    action: bpy.props.EnumProperty(items=[("OPERATOR","Operator","Operator"),
                                    ("PANEL","Panel","Panel"),
                                    ("MENU","Menu","Menu"),
                                    ("PIE_MENU","Pie Menu","Pie Menu")],
                                name="Shortcut Type",
                                description="The type of action to run from this shortcut",
                                update=reset_inputs)
    
    parent_type: bpy.props.EnumProperty(name="Parent Type",
                                description="Use a custom panel as a parent",
                                items=[("BLENDER", "Blender", "Blender", "BLENDER", 0),
                                        ("CUSTOM", "Custom", "Custom", "FILE_SCRIPT", 1)],
                                update=reset_inputs)
    
    def update_picked(self,context):
        if self.picked:
            elem = eval("bpy.types." + self.picked)
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
            
    picked: bpy.props.StringProperty(update=update_picked)
    
    panel: bpy.props.StringProperty(name="Panel",
                                description="The panel to open when the key is pressed",
                                update=SN_ScriptingBaseNode._evaluate)
    
    menu: bpy.props.StringProperty(name="Menu",
                                description="The menu to open when the key is pressed",
                                update=SN_ScriptingBaseNode._evaluate)
    
    pie: bpy.props.StringProperty(name="Pie Menu",
                                description="The pie menu to open when the key is pressed",
                                update=SN_ScriptingBaseNode._evaluate)

    def create_inputs(self, op_rna):
        """ Create inputs for operator """
        for prop in op_rna.properties:
            if not prop.identifier in ["rna_type", "settings"]:
                inp = self.add_input_from_property(prop)
                if inp:
                    inp.can_be_disabled = not prop.is_required
                    inp.disabled = not prop.is_required

    def update_pasted_operator(self, context):
        self.inputs.clear()
        
        if self.pasted_operator:
            op = eval(self.pasted_operator.split("(")[0])
            op_rna = op.get_rna_type()
            self.create_inputs(op_rna)
        self._evaluate(context)
    
    pasted_operator: bpy.props.StringProperty(name="Operator",
                                description="The operator to run when the key is pressed",
                                update=update_pasted_operator)
    
    keep_open: bpy.props.BoolProperty(name="Keep Open",
                                description="Keep the panel open after a property is changed",
                                default=True,
                                update=SN_ScriptingBaseNode._evaluate)
    
    ref_ntree: bpy.props.PointerProperty(type=bpy.types.NodeTree,
                                name="Panel Node Tree",
                                description="The node tree to select the panel from",
                                poll=SN_ScriptingBaseNode.ntree_poll,
                                update=SN_ScriptingBaseNode._evaluate)
    
    ref_SN_PanelNode: bpy.props.StringProperty(name="Panel",
                                description="The panel to open with this shortcut",
                                update=SN_ScriptingBaseNode._evaluate)
    
    ref_SN_MenuNode: bpy.props.StringProperty(name="Menu",
                                description="The menu to open with this shortcut",
                                update=SN_ScriptingBaseNode._evaluate)
    
    ref_SN_PieMenuNode: bpy.props.StringProperty(name="Menu",
                                description="The menu to open with this shortcut",
                                update=SN_ScriptingBaseNode._evaluate)
    
    def on_ref_update(self, node, data=None):
        if node.bl_idname in ["SN_PanelNode", "SN_MenuNode", "SN_PieMenuNode"]:
            self._evaluate(bpy.context)
        elif node.bl_idname in ["SN_OperatorNode", "SN_ModalOperatorNode"]:
            on_operator_ref_update(self, node, data, self.ref_ntree, self.ref_SN_OperatorNode, 0)
            
    def update_custom_operator(self, context):
        """ Updates the nodes settings when a new parent panel is selected """
        self.inputs.clear()
        if self.ref_ntree and self.ref_SN_OperatorNode in self.ref_ntree.nodes:
            parent = self.ref_ntree.nodes[self.ref_SN_OperatorNode]
            for prop in parent.properties:
                if prop.property_type in ["Integer", "Float", "Boolean"] and prop.settings.is_vector:
                    socket = self._add_input(self.socket_names[prop.property_type + " Vector"], prop.name)
                    socket.size = prop.settings.size
                    socket.can_be_disabled = True
                else:
                    self._add_input(self.socket_names[prop.property_type], prop.name).can_be_disabled = True
                
        self._evaluate(context)
    
    ref_SN_OperatorNode: bpy.props.StringProperty(name="Operator",
                                description="The operator to run with this shortcut",
                                update=update_custom_operator)

    def evaluate(self, context):
        if self.key:
            input_code = ""
            operator = ""
            if self.action == "PANEL":
                if self.parent_type == "BLENDER" and self.panel:
                    operator = "wm.call_panel"
                    input_code = f"kmi.properties.name = '{self.panel}'\n"
                    input_code += f"kmi.properties.keep_open = {self.keep_open}\n"
                elif self.parent_type == "CUSTOM" and self.ref_ntree and self.ref_SN_PanelNode in self.ref_ntree.nodes:
                    operator = "wm.call_panel"
                    node = self.ref_ntree.nodes[self.ref_SN_PanelNode]
                    input_code = f"kmi.properties.name = '{node.last_idname}'\n"
                    input_code += f"kmi.properties.keep_open = {self.keep_open}\n"
            elif self.action == "MENU":
                if self.parent_type == "BLENDER" and self.menu:
                    operator = "wm.call_menu"
                    input_code = f"kmi.properties.name = '{self.menu}'\n"
                elif self.parent_type == "CUSTOM" and self.ref_ntree and self.ref_SN_MenuNode in self.ref_ntree.nodes:
                    operator = "wm.call_menu"
                    node = self.ref_ntree.nodes[self.ref_SN_MenuNode]
                    input_code = f"kmi.properties.name = '{node.idname}'\n"
            elif self.action == "PIE_MENU":
                if self.parent_type == "BLENDER" and self.pie:
                    operator = "wm.call_menu_pie"
                    input_code = f"kmi.properties.name = '{self.pie}'\n"
                elif self.parent_type == "CUSTOM" and self.ref_ntree and self.ref_SN_PieMenuNode in self.ref_ntree.nodes:
                    operator = "wm.call_menu_pie"
                    node = self.ref_ntree.nodes[self.ref_SN_PieMenuNode]
                    input_code = f"kmi.properties.name = '{node.idname}'\n"
            elif self.action == "OPERATOR":
                if self.parent_type == "BLENDER" and self.pasted_operator:
                    if not self.pasted_operator: return
                    operator = self.pasted_operator.split("(")[0].replace("bpy.ops.", "")
                    op = eval(self.pasted_operator.split("(")[0])
                    op_rna = op.get_rna_type()
                    for inp in self.inputs:
                        if not inp.disabled:
                            for prop in op_rna.properties:
                                if (self.version == 0 and (prop.name and prop.name == inp.name) or (not prop.name and prop.identifier.replace("_", " ").title() == inp.name)) \
                                    or (self.version == 1 and (inp.name.replace(" ", "_").lower() == prop.identifier)):
                                    self.code += "\n" + f"op.{prop.identifier} = {inp.python_value}"
                                    input_code += f"kmi.properties.{prop.identifier} = {inp.python_value}\n"
                elif self.parent_type == "CUSTOM" and self.ref_ntree and self.ref_SN_OperatorNode in self.ref_ntree.nodes:
                    node = self.ref_ntree.nodes[self.ref_SN_OperatorNode]
                    operator = f"sna.{node.operator_python_name}"
                    for inp in self.inputs:
                        if not inp.disabled:
                            for prop in node.properties:
                                if prop.name == inp.name:
                                    input_code += f"kmi.properties.{prop.python_name} = {inp.python_value}\n"
            if operator:
                self.code_register = f"""
                    kc = bpy.context.window_manager.keyconfigs.addon
                    km = kc.keymaps.new(name='{space_names[self.space]}', space_type='{self.space}')
                    kmi = km.keymap_items.new('{operator}', '{self.key}', '{self.value}',
                        ctrl={self.ctrl}, alt={self.alt}, shift={self.shift}, repeat={self.repeat})
                    {f'kmi.direction = "{self.direction}"' if self.value == "CLICK_DRAG" else ''}
                    {self.indent(input_code, 5)}
                    addon_keymaps['{self.static_uid}'] = (km, kmi)
                """

    def draw_node(self, context, layout):
        row = layout.row(align=True)
        row.prop(self, "space", text="")
        row.prop(self, "value", text="")
        
        if self.value == "CLICK_DRAG":
            layout.prop(self, "direction", text="")
        
        layout.operator("sn.record_key", text=self.key, depress=self.recording).node = self.name
        row = layout.row(align=True)
        row.prop(self,"ctrl", toggle=True)
        row.prop(self,"shift", toggle=True)
        row.prop(self,"alt", toggle=True)
        layout.prop(self, "repeat")
        layout.separator()

        row = layout.row(align=True)
        row.prop(self, "name", text="")
        row.operator("sn.find_referencing_nodes", text="", icon="VIEWZOOM").node = self.name
        layout.separator()

        row = layout.row(align=True)
        row.prop(self,"action", text="")
        row.prop(self,"parent_type", text="", icon_only=True)

        parent_tree = self.ref_ntree if self.ref_ntree else self.node_tree

        if self.action == "PANEL":
            if self.parent_type == "BLENDER":
                name = self.panel.replace("_", " ").title() if self.panel else "Select Panel"
                op = layout.operator("sn.pick_interface", text=name, icon="EYEDROPPER")
                op.node = self.name
                op.selection = "PANELS"
            else:
                row = layout.row(align=True)
                row.prop_search(self, "ref_ntree", bpy.data, "node_groups", text="")
                subrow = row.row(align=True)
                subrow.enabled = self.ref_ntree != None
                subrow.prop_search(self, "ref_SN_PanelNode", parent_tree.node_collection("SN_PanelNode"), "refs", text="", icon="VIEWZOOM")

                subrow = row.row()
                subrow.enabled = self.ref_ntree != None and self.ref_SN_PanelNode in self.ref_ntree.nodes
                op = subrow.operator("sn.find_node", text="", icon="RESTRICT_SELECT_OFF", emboss=False)
                op.node_tree = self.ref_ntree.name if self.ref_ntree else ""
                op.node = self.ref_SN_PanelNode

            layout.prop(self, "keep_open")

        elif self.action == "MENU":
            if self.parent_type == "BLENDER":
                name = self.menu.replace("_", " ").title() if self.menu else "Select Menu"
                op = layout.operator("sn.pick_interface", text=name, icon="EYEDROPPER")
                op.node = self.name
                op.selection = "MENUS"
            else:
                row = layout.row(align=True)
                row.prop_search(self, "ref_ntree", bpy.data, "node_groups", text="")
                subrow = row.row(align=True)
                subrow.enabled = self.ref_ntree != None
                subrow.prop_search(self, "ref_SN_MenuNode", parent_tree.node_collection("SN_MenuNode"), "refs", text="", icon="VIEWZOOM")

                subrow = row.row()
                subrow.enabled = self.ref_ntree != None and self.ref_SN_MenuNode in self.ref_ntree.nodes
                op = subrow.operator("sn.find_node", text="", icon="RESTRICT_SELECT_OFF", emboss=False)
                op.node_tree = self.ref_ntree.name if self.ref_ntree else ""
                op.node = self.ref_SN_MenuNode

        elif self.action == "PIE_MENU":
            if self.parent_type == "BLENDER":
                name = self.pie.replace("_"," ").title() if self.pie else "Select Pie Menu"
                op = layout.operator("sn.pick_interface", text=name, icon="EYEDROPPER")
                op.node = self.name
                op.selection = "MENUS"
            else:
                row = layout.row(align=True)
                row.prop_search(self, "ref_ntree", bpy.data, "node_groups", text="")
                subrow = row.row(align=True)
                subrow.enabled = self.ref_ntree != None
                subrow.prop_search(self, "ref_SN_PieMenuNode", parent_tree.node_collection("SN_PieMenuNode"), "refs", text="", icon="VIEWZOOM")

                subrow = row.row()
                subrow.enabled = self.ref_ntree != None and self.ref_SN_PieMenuNode in self.ref_ntree.nodes
                op = subrow.operator("sn.find_node", text="", icon="RESTRICT_SELECT_OFF", emboss=False)
                op.node_tree = self.ref_ntree.name if self.ref_ntree else ""
                op.node = self.ref_SN_PieMenuNode
                
        elif self.action == "OPERATOR":
            if self.parent_type == "BLENDER":
                name = self.pasted_operator.split("(")[0].split(".")[-1].replace("_"," ").title() if self.pasted_operator else "Paste Operator"
                op = layout.operator("sn.paste_operator", text=name, icon="PASTEDOWN")
                op.node_tree = self.node_tree.name
                op.node = self.name
            else:
                row = layout.row(align=True)
                row.prop_search(self, "ref_ntree", bpy.data, "node_groups", text="")
                subrow = row.row(align=True)
                subrow.enabled = self.ref_ntree != None
                subrow.prop_search(self, "ref_SN_OperatorNode", parent_tree.node_collection("SN_OperatorNode"), "refs", text="", icon="VIEWZOOM")

                subrow = row.row()
                subrow.enabled = self.ref_ntree != None and self.ref_SN_OperatorNode in self.ref_ntree.nodes
                op = subrow.operator("sn.find_node", text="", icon="RESTRICT_SELECT_OFF", emboss=False)
                op.node_tree = self.ref_ntree.name if self.ref_ntree else ""
                op.node = self.ref_SN_OperatorNode
