import bpy
from ..base_node import SN_ScriptingBaseNode



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
                                         ("ANY","Any","The action will run with any of the above ways")],
                                  update=SN_ScriptingBaseNode._evaluate)
    
    repeat: bpy.props.BoolProperty(name="Repeat Key",
                                   description="Repeat the action when the key is held down",
                                   default=False,
                                   update=SN_ScriptingBaseNode._evaluate)
    
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
                                update=SN_ScriptingBaseNode._evaluate)
    
    parent_type: bpy.props.EnumProperty(name="Parent Type",
                                description="Use a custom panel as a parent",
                                items=[("BLENDER", "Blender", "Blender", "BLENDER", 0),
                                        ("CUSTOM", "Custom", "Custom", "FILE_SCRIPT", 1)],
                                update=SN_ScriptingBaseNode._evaluate)
    
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
    
    pasted_operator: bpy.props.StringProperty(name="Operator",
                                description="The operator to run when the key is pressed",
                                update=SN_ScriptingBaseNode._evaluate)
    
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
    
    ref_SN_OperatorNode: bpy.props.StringProperty(name="Operator",
                                description="The operator to run with this shortcut",
                                update=SN_ScriptingBaseNode._evaluate)

    def evaluate(self, context):
        self.code_register = f"""
            kc = bpy.context.window_manager.keyconfigs.addon
            km = kc.keymaps.new(name='Window', space_type='EMPTY', region_type='WINDOW')
            kmi = km.keymap_items.new('sn.force_compile',
                                    'F6',
                                    'PRESS',
                                    ctrl=False,
                                    alt=False,
                                    shift=False)
            kmi.active = True
            addon_keymaps.append((km, kmi))
        """

    def draw_node(self, context, layout):
        row = layout.row(align=True)
        row.prop(self, "space", text="")
        row.prop(self, "value", text="")
        
        layout.operator("sn.record_key", text=self.key, depress=self.recording).node = self.name
        row = layout.row(align=True)
        row.prop(self,"ctrl", toggle=True)
        row.prop(self,"shift", toggle=True)
        row.prop(self,"alt", toggle=True)
        layout.prop(self, "repeat")
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
                layout.prop_search(self, "ref_SN_PanelNode", parent_tree.node_collection("SN_PanelNode"), "refs", text="", icon="VIEWZOOM")
            layout.prop(self, "keep_open")

        elif self.action == "MENU":
            if self.parent_type == "BLENDER":
                name = self.menu.replace("_", " ").title() if self.menu else "Select Menu"
                op = layout.operator("sn.pick_interface", text=name, icon="EYEDROPPER")
                op.node = self.name
                op.selection = "MENUS"
            else: # TODO menu node
                layout.prop_search(self, "ref_SN_PanelNode", parent_tree.node_collection("SN_PanelNode"), "refs", text="", icon="VIEWZOOM")

        elif self.action == "PIE_MENU":
            if self.parent_type == "BLENDER":
                name = self.pie.replace("_"," ").title() if self.pie else "Select Pie Menu"
                op = layout.operator("sn.pick_interface", text=name, icon="EYEDROPPER")
                op.node = self.name
                op.selection = "MENUS"
            else: # TODO pie menu
                layout.prop_search(self, "ref_SN_PanelNode", parent_tree.node_collection("SN_PanelNode"), "refs", text="", icon="VIEWZOOM")
                
        elif self.action == "OPERATOR":
            if self.parent_type == "BLENDER":
                name = self.pasted_operator.split(".")[-1].split("(")[0].replace("_"," ").title() if self.pasted_operator else "Paste Operator"
                op = layout.operator("sn.paste_operator", text=name, icon="PASTEDOWN")
                op.node_tree = self.node_tree.name
                op.node = self.name
            else:
                layout.prop_search(self, "ref_SN_OperatorNode", parent_tree.node_collection("SN_OperatorNode"), "refs", text="", icon="VIEWZOOM")
