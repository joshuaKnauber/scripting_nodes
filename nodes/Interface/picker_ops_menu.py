import bpy



registered_menus = []



def register_dummy_interface(ntree, node, menu):
    func_name  = f"sna_dummy_{menu.bl_rna.identifier}"
    label = getattr(menu, "bl_label", menu.bl_rna.identifier.replace('_PT_', ' ').replace('_', ' ').title())
    menu = f"""
def {func_name}(self, context):
    layout = self.layout
    row = layout.row()
    row.alert = True
    op = row.operator("sn.pick_menu_location", text="Select '{label}'", icon="EYEDROPPER")
    op.node_tree = "{ntree}"
    op.node = "{node}"
    op.menu = "{menu.bl_rna.identifier}"
    
bpy.types.{menu.bl_rna.identifier}.append({func_name})
registered_menus.append([bpy.types.{menu.bl_rna.identifier}, {func_name}])
"""
    try: exec(menu, globals())
    except: pass
     


class SN_OT_ActivateMenuPicker(bpy.types.Operator):
    bl_idname = "sn.activate_menu_picker"
    bl_label = "Select Menu Location"
    bl_description = "Select the location of this menu in the Interface"
    bl_options = {"REGISTER", "INTERNAL"}

    node_tree: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})
    node: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    @classmethod
    def poll(cls, context):
        return not context.scene.sn.picker_active

    def execute(self, context):
        # register menus
        for menu in bpy.types.Menu.__subclasses__():
            register_dummy_interface(self.node_tree, self.node,menu)
        
        # redraw screen
        for area in context.screen.areas:
            area.tag_redraw()

        # set picker active
        context.scene.sn.picker_active = True
        return {"FINISHED"}
     


class SN_OT_PickMenuLocation(bpy.types.Operator):
    bl_idname = "sn.pick_menu_location"
    bl_label = "Pick Location"
    bl_description = "Pick this location to put the menu into"
    bl_options = {"REGISTER", "INTERNAL"}

    node_tree: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})
    node: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    menu: bpy.props.StringProperty(options={"SKIP_SAVE", "HIDDEN"})

    def execute(self, context):
        # find node and set properties
        if self.node_tree in bpy.data.node_groups:
            ntree = bpy.data.node_groups[self.node_tree]
            if self.node in ntree.nodes:
                node = ntree.nodes[self.node]
                node.menu_parent = self.menu
                
        # unregister menus
        for menu in registered_menus:
            try: menu[0].remove(menu[1])
            except: pass

        # reset saves and picker
        registered_menus.clear()
        context.scene.sn.picker_active = False
        return {"FINISHED"}
