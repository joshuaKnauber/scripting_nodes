import bpy
import json
from ...interface.menu.rightclick import construct_from_attached_property


class SN_OT_CreateProperty(bpy.types.Operator):
    bl_idname = "sn.add_property"
    bl_label = "Add Property"
    bl_description = "Adds a new property to this addon"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def execute(self, context):
        addon_tree = context.scene.sn.addon_tree()

        variable = addon_tree.sn_properties.add()
        variable.is_property = True
        variable.node_tree = addon_tree
        variable.name = "New Property"
        
        addon_tree.sn_property_index = len(addon_tree.sn_properties)-1
        return {"FINISHED"}



class SN_OT_RemoveProperty(bpy.types.Operator):
    bl_idname = "sn.remove_property"
    bl_label = "Remove Property"
    bl_description = "Removes this property from the addon"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    @classmethod
    def poll(cls, context):
        addon_tree = context.scene.sn.addon_tree()
        return len(addon_tree.sn_properties) > 0

    def execute(self, context):
        addon_tree = context.scene.sn.addon_tree()
        addon_tree.sn_properties.remove(addon_tree.sn_property_index)
        if addon_tree.sn_property_index > 0:
            addon_tree.sn_property_index -= 1
        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)
    
    
    
def place_center(context,node):
    for region in context.area.regions:
        if region.type == "WINDOW":
            loc = region.view2d.region_to_view(region.width//2,region.height//2)
            node.location = loc
    
    
    
class SN_OT_AddPropertyGetter(bpy.types.Operator):
    bl_idname = "sn.add_prop_getter"
    bl_label = "Add Getter"
    bl_description = "Adds a node which gives you the value of this variable"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}
    
    getter_type: bpy.props.EnumProperty(items=[("PROPERTY","Property","Normal property getter"),
                                                ("INTERFACE","Interface","Interface property")],
                                        options={"SKIP_SAVE"},
                                        name="Getter Type",
                                        description="The getter type for your property")

    def execute(self, context):
        addon_tree = context.scene.sn.addon_tree()
        graph_tree = addon_tree.sn_graphs[addon_tree.sn_graph_index].node_tree
        prop = addon_tree.sn_properties[addon_tree.sn_property_index]

        if self.getter_type == "PROPERTY":
            node = graph_tree.nodes.new("SN_GetPropertyNode")
        elif self.getter_type == "INTERFACE":
            node = graph_tree.nodes.new("SN_DisplayPropertyNode")
        node.copied_path = construct_from_attached_property(prop.attach_property_to,prop.attach_property_to,prop)
        
        place_center(context, node)
        return {"FINISHED"}
    
    def draw(self,context):
        self.layout.prop(self,"getter_type",expand=True)
    
    def invoke(self,context,event):
        return context.window_manager.invoke_props_dialog(self)
    
    

class SN_OT_AddPropertySetter(bpy.types.Operator):
    bl_idname = "sn.add_prop_setter"
    bl_label = "Add Setter"
    bl_description = "Adds a node which lets you set the value of this variable"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def execute(self, context):
        addon_tree = context.scene.sn.addon_tree()
        graph_tree = addon_tree.sn_graphs[addon_tree.sn_graph_index].node_tree
        prop = addon_tree.sn_properties[addon_tree.sn_property_index]

        node = graph_tree.nodes.new("SN_SetPropertyNode")
        
        node.copied_path = construct_from_attached_property(prop.attach_property_to,prop.attach_property_to,prop)
        return {"FINISHED"}
    
    

class SN_OT_AddEnumItem(bpy.types.Operator):
    bl_idname = "sn.add_enum_item"
    bl_label = "Add Enum Item"
    bl_description = "Adds an item to this enum property"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}
    
    node: bpy.props.StringProperty(options={"SKIP_SAVE"},default="")
    node_attr: bpy.props.StringProperty(options={"SKIP_SAVE"},default="")
    node_index: bpy.props.IntProperty(options={"SKIP_SAVE"},default=0)
    
    def execute(self, context):
        if self.node:
            prop = getattr(context.space_data.node_tree.nodes[self.node],self.node_attr)[self.node_index]
        else:
            addon_tree = context.scene.sn.addon_tree()
            prop = addon_tree.sn_properties[addon_tree.sn_property_index]

        prop.enum_items.add()
        if self.node:
            prop.trigger_update(context)
        return {"FINISHED"}
    
    

class SN_OT_RemoveEnumItem(bpy.types.Operator):
    bl_idname = "sn.remove_enum_item"
    bl_label = "Remove Enum Item"
    bl_description = "Removes this item from this enum property"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}
    
    node: bpy.props.StringProperty(options={"SKIP_SAVE"},default="")
    node_attr: bpy.props.StringProperty(options={"SKIP_SAVE"},default="")
    node_index: bpy.props.IntProperty(options={"SKIP_SAVE"},default=0)
    
    index: bpy.props.IntProperty()

    def execute(self, context):
        if self.node:
            prop = getattr(context.space_data.node_tree.nodes[self.node],self.node_attr)[self.node_index]
        else:
            addon_tree = context.scene.sn.addon_tree()
            prop = addon_tree.sn_properties[addon_tree.sn_property_index]
            
        prop.enum_items.remove(self.index)
        if self.node:
            prop.trigger_update(context)
        return {"FINISHED"}
    
    

class SN_OT_MoveEnumItem(bpy.types.Operator):
    bl_idname = "sn.move_enum_item"
    bl_label = "Move Enum Item"
    bl_description = "Moves this item in this enum property"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}
    
    node: bpy.props.StringProperty(options={"SKIP_SAVE"},default="")
    node_attr: bpy.props.StringProperty(options={"SKIP_SAVE"},default="")
    node_index: bpy.props.IntProperty(options={"SKIP_SAVE"},default=0)
    
    index: bpy.props.IntProperty()
    down: bpy.props.BoolProperty()

    def execute(self, context):
        if self.node:
            prop = getattr(context.space_data.node_tree.nodes[self.node],self.node_attr)[self.node_index]
        else:
            addon_tree = context.scene.sn.addon_tree()
            prop = addon_tree.sn_properties[addon_tree.sn_property_index]
            
        if self.down and self.index < len(prop.enum_items)-1:
            prop.enum_items.move(self.index, self.index+1)
        elif not self.down and self.index > 0:
            prop.enum_items.move(self.index, self.index-1)
            
        if self.node:
            prop.trigger_update(context)
        return {"FINISHED"}