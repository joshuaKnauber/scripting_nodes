import bpy
import json
from ...interface.menu.rightclick import construct_from_attached_property, construct_from_property


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
        prop = addon_tree.sn_properties[addon_tree.sn_property_index]
        for graph in addon_tree.sn_graphs:
            for node in graph.node_tree.nodes:
                if node.bl_idname in ["SN_GetPropertyNode", "SN_SetPropertyNode", "SN_DisplayPropertyNode", "SN_UpdatePropertyNode"]:
                    node.on_outside_update(construct_from_attached_property(prop.attach_property_to,prop.attach_property_to,prop, removed=True))

        addon_tree.sn_properties.remove(addon_tree.sn_property_index)
        if addon_tree.sn_property_index > 0:
            addon_tree.sn_property_index -= 1

        return {"FINISHED"}

    def invoke(self, context, event):
        return context.window_manager.invoke_confirm(self, event)
    
    
    
class SN_OT_AddPropertyGetter(bpy.types.Operator):
    bl_idname = "sn.add_prop_getter"
    bl_label = "Add Getter"
    bl_description = "Adds a node which gives you the value of this variable"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def get_items(self, context):
        items = [("PROPERTY","Property","Normal property getter"),("INTERFACE","Interface","Interface property")]
        addon_tree = context.scene.sn.addon_tree()
        if not addon_tree.sn_properties[addon_tree.sn_property_index].has_update():
            items.append(("UPDATE", "Update", "Update Function"))
        return items

    getter_type: bpy.props.EnumProperty(items=get_items,
                                        options={"SKIP_SAVE"},
                                        name="Getter Type",
                                        description="The getter type for your property")

    def execute(self, context):
        addon_tree = context.scene.sn.addon_tree()
        graph_tree = addon_tree.sn_graphs[addon_tree.sn_graph_index].node_tree
        prop = addon_tree.sn_properties[addon_tree.sn_property_index]

        if self.getter_type == "PROPERTY":
            bpy.ops.node.add_node("INVOKE_DEFAULT",type="SN_GetPropertyNode",use_transform=True)
        elif self.getter_type == "INTERFACE":
            bpy.ops.node.add_node("INVOKE_DEFAULT",type="SN_DisplayPropertyNode",use_transform=True)
        elif self.getter_type == "UPDATE":
            bpy.ops.node.add_node("INVOKE_DEFAULT",type="SN_UpdatePropertyNode",use_transform=True)
            graph_tree.nodes.active.wrong_add = False

        graph_tree.nodes.active.copied_path = construct_from_attached_property(prop.attach_property_to,prop.attach_property_to,prop)
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

        bpy.ops.node.add_node("INVOKE_DEFAULT",type="SN_SetPropertyNode",use_transform=True)
        
        graph_tree.nodes.active.copied_path = construct_from_attached_property(prop.attach_property_to,prop.attach_property_to,prop)
        return {"FINISHED"}
    
    
class SN_OT_MoveProperty(bpy.types.Operator):
    bl_idname = "sn.move_property"
    bl_label = "Move Property"
    bl_description = "Moves this property"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}
    
    up: bpy.props.BoolProperty()

    def execute(self, context):
        addon_tree = context.scene.sn.addon_tree()
        
        if (self.up):
            addon_tree.sn_properties.move(addon_tree.sn_property_index,addon_tree.sn_property_index-1)
            addon_tree.sn_property_index -= 1
        else:
            addon_tree.sn_properties.move(addon_tree.sn_property_index,addon_tree.sn_property_index+1)
            addon_tree.sn_property_index += 1
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

        item = prop.enum_items.add()
        item.node = self.node
        item.node_attr = self.node_attr
        item.node_index = self.node_index

        if self.node:
            prop.update_enum(context)
        else:
            for graph in context.scene.sn.addon_tree().sn_graphs:
                for node in graph.node_tree.nodes:
                    if node.bl_idname == "SN_SetPropertyNode":
                        if prop.use_self:
                            path = "self" if prop.find_node(context) else "context.preferences.addons[__name__.partition('.')[0]].preferences"
                            node.on_outside_update(construct_from_property(path,prop, prop.from_node_uid))
                        else:
                            node.on_outside_update(construct_from_attached_property(prop.attach_property_to,prop.attach_property_to,prop))

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
            prop.update_enum(context)
        else:
            for graph in context.scene.sn.addon_tree().sn_graphs:
                for node in graph.node_tree.nodes:
                    if node.bl_idname == "SN_SetPropertyNode":
                        if prop.use_self:
                            path = "self" if prop.find_node(context) else "context.preferences.addons[__name__.partition('.')[0]].preferences"
                            node.on_outside_update(construct_from_property(path,prop, prop.from_node_uid))
                        else:
                            node.on_outside_update(construct_from_attached_property(prop.attach_property_to,prop.attach_property_to,prop))

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
            prop.update_enum(context)
        return {"FINISHED"}