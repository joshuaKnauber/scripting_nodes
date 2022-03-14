import bpy



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
    
    
def sn_append_interface(self, context):
    row = self.layout.row()
    row.alert = True
    op = row.operator("sn.select_interface_add",text="Select",icon="CHECKMARK")
    op.idname = self.bl_idname
    
    
    
remove_interfaces = []
picker_node = None

    

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