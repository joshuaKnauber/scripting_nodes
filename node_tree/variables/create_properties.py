import bpy
import json


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
    
    
    
class SN_OT_AddPropertyGetter(bpy.types.Operator):
    bl_idname = "sn.add_prop_getter"
    bl_label = "Add Getter"
    bl_description = "Adds a node which gives you the value of this variable"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def execute(self, context):
        addon_tree = context.scene.sn.addon_tree()
        graph_tree = addon_tree.sn_graphs[addon_tree.sn_graph_index].node_tree
        prop = addon_tree.sn_properties[addon_tree.sn_property_index]

        node = graph_tree.nodes.new("SN_GetPropertyNode")
        path_details = {
            "path": f"{prop.attach_property_to}[\"\"].{prop.identifier}",
            "prop_name": prop.name,
            "prop_identifier": prop.identifier,
            "prop_type": prop.var_type,
            "prop_array_length": prop.vector_size if prop.is_vector else -1,
            "path_parts": [f"{{\"is_numeric\"=False,\"data_type\"=\"bpy.types.{prop.attach_property_to}\",\"name\"=\"{prop.name}\"}}",
                           prop.identifier]
        }
        node.copied_path = json.dumps(path_details)
        return {"FINISHED"}
    
    

class SN_OT_AddPropertySetter(bpy.types.Operator):
    bl_idname = "sn.add_prop_setter"
    bl_label = "Add Setter"
    bl_description = "Adds a node which lets you set the value of this variable"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def execute(self, context):
        addon_tree = context.scene.sn.addon_tree()
        graph_tree = addon_tree.sn_graphs[addon_tree.sn_graph_index].node_tree

        node = graph_tree.nodes.new("SN_TestNode")
        return {"FINISHED"}
    
    

class SN_OT_AddEnumItem(bpy.types.Operator):
    bl_idname = "sn.add_enum_item"
    bl_label = "Add Enum Item"
    bl_description = "Adds an item to this enum property"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}

    def execute(self, context):
        addon_tree = context.scene.sn.addon_tree()

        prop = addon_tree.sn_properties[addon_tree.sn_property_index]
        prop.enum_items.add()
        return {"FINISHED"}
    
    

class SN_OT_RemoveEnumItem(bpy.types.Operator):
    bl_idname = "sn.remove_enum_item"
    bl_label = "Remove Enum Item"
    bl_description = "Removes this item from this enum property"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}
    
    index: bpy.props.IntProperty()

    def execute(self, context):
        addon_tree = context.scene.sn.addon_tree()

        prop = addon_tree.sn_properties[addon_tree.sn_property_index]
        prop.enum_items.remove(self.index)
        return {"FINISHED"}
    
    

class SN_OT_MoveEnumItem(bpy.types.Operator):
    bl_idname = "sn.move_enum_item"
    bl_label = "Move Enum Item"
    bl_description = "Moves this item in this enum property"
    bl_options = {"REGISTER", "UNDO", "INTERNAL"}
    
    index: bpy.props.IntProperty()
    down: bpy.props.BoolProperty()

    def execute(self, context):
        addon_tree = context.scene.sn.addon_tree()

        prop = addon_tree.sn_properties[addon_tree.sn_property_index]
        if self.down and self.index < len(prop.enum_items)-1:
            prop.enum_items.move(self.index, self.index+1)
        elif not self.down and self.index > 0:
            prop.enum_items.move(self.index, self.index-1)
        return {"FINISHED"}