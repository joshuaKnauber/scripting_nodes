import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup



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
    
    
    key: bpy.props.StringProperty(name="Key",default="Y")

    recording: bpy.props.BoolProperty(name="Recording",default=False)

    ctrl: bpy.props.BoolProperty(name="Ctrl",
                                  description="If the ctrl key has to be pressed",
                                  default=False)
    
    alt: bpy.props.BoolProperty(name="Alt",
                                  description="If the alt key has to be pressed",
                                  default=False)
    
    shift: bpy.props.BoolProperty(name="Shift",
                                  description="If the shift key has to be pressed",
                                  default=False)
    
    value: bpy.props.EnumProperty(name="Value",
                                  description="The way the key has to be pressed",
                                  items=[("PRESS","On Press","The action is run when the key is pressed once"),
                                         ("RELEASE","On Release","The action is run when the key is released"),
                                         ("CLICK","On Click","The action is run when the mouse button is clicked once"),
                                         ("DOUBLE_CLICK","On Double Click","The action is run when the mouse button is clicked twice"),
                                         ("ANY","Any","The action will run with any of the above ways")])
    
    repeat: bpy.props.BoolProperty(name="Repeat Key",
                                   description="Repeat the action when the key is held down",
                                   default=False)
    
    space: bpy.props.EnumProperty(name="Space",
                                  description="The space where this shortcut is active",
                                  items=get_spaces)
    
    
    action: bpy.props.EnumProperty(name="Action",
                                   description="The type of action to be performed",
                                   items=[("OPERATOR","Operator","Run an operator when the key is pressed"),
                                          ("PANEL","Panel","Open a panel when the key is pressed"),
                                          ("MENU","Menu","Open a menu when the key is pressed"),
                                          ("PIE_MENU","Pie","Open a pie menu when the key is pressed")])
    
    keep_open: bpy.props.BoolProperty(name="Keep Open",
                                      description="Keep the panel open after a property is changed",
                                      default=True)
    
    use_internal: bpy.props.BoolProperty(name="Use Internal",
                                         description="Uses the internal ones from blender instead of your custom ones",
                                         default=False,
                                         update=update_use_internal)
    
    panel: bpy.props.StringProperty(name="Panel",
                                    description="The panel to open when the key is pressed")
    

    def draw_node(self,context,layout):
        row = layout.row(align=True)
        row.prop(self,"space",text="")
        row.prop(self,"value",text="")
        layout.operator("sn.record_key",text=self.key,depress=self.recording).node = self.name
        row = layout.row(align=True)
        row.prop(self,"ctrl",toggle=True)
        row.prop(self,"shift",toggle=True)
        row.prop(self,"alt",toggle=True)
        layout.prop(self,"repeat")
        layout.separator()

        row = layout.row()
        row.prop(self,"action",text="")
        if self.use_internal:
            row.prop(self,"use_internal",text="",icon="BLENDER",emboss=False)
        else:
            row.prop(self,"use_internal",text="",icon_value=bpy.context.scene.sn_icons[ "serpens" ].icon_id,emboss=False)
        if self.action == "PANEL":
            layout.prop_search(self,"panel",self.addon_tree.sn_nodes["SN_PanelNode"],"items",text="",icon="VIEWZOOM")
            layout.prop(self,"keep_open")


    def code_imperative(self, context):
        return {
            "code": f"""
                    addon_keymaps = []
                    """
        }
        
        
    def code_evaluate(self, context, touched_socket):
        
        names = {
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
        
        action = "mesh.primitive_monkey_add"
        properties = []

        if self.action == "PANEL":
            action = "wm.call_panel"
            panel = "RENDER_PT_dimensions"
            if self.use_internal:
                pass
            elif self.action == "PANEL" and self.panel in self.addon_tree.sn_nodes["SN_PanelNode"].items:
                panel = self.addon_tree.sn_nodes["SN_PanelNode"].items[self.panel].node().idname()
            properties.append(f"kmi.properties.name = \"{panel}\"\n")
            properties.append(f"kmi.properties.keep_open = {self.keep_open}\n")
            
        
        return {
            "code": f"""
                    def register_key_{self.uid}():
                        kc = bpy.context.window_manager.keyconfigs.addon
                        if kc:
                            km = kc.keymaps.new(name="{names[self.space]}", space_type="{self.space}")
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