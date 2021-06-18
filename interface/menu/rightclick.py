import bpy
import json



def construct_from_property(path,prop, created_from="", removed=False):
    size = -1
    if prop.is_vector:
        size = prop.vector_size
    items = ""
    data = {
        "data_block": {
            "name": "",
            "type": ""
        },
        "group_path": path,
        "property": {
            "name": prop.name,
            "identifier": prop.identifier,
            "type": prop.var_type,
            "subtype": prop.property_subtype,
            "size": size,
            "items": prop.enum_string(),
            "is_set": False,
            "created_from": created_from,
            "removed": removed
        }
    }
    return json.dumps(data)
    

    
def construct_from_attached_property(db_name,db_type,prop, removed=False):
    data = json.loads(construct_from_property("",prop,"SN_CUSTOM", removed))
    data["data_block"]["name"] = db_name
    data["data_block"]["type"] = db_type
    return json.dumps(data)



class SN_OT_CopyProperty(bpy.types.Operator):
    bl_idname = "sn.copy_space_property"
    bl_label = "Copy Space Property"
    bl_description = "Copy the property from this space"
    bl_options = {"REGISTER","UNDO","INTERNAL"}
    
    origin: bpy.props.EnumProperty(items=[("DEFAULT","DEFAULT","DEFAULT"),
                                          ("SPACE_DATA","SPACE_DATA","SPACE_DATA"),
                                          ("SPACE","SPACE","SPACE"),
                                          ("PREFERENCES","PREFERENCES","PREFERENCES")],
                                   options={"HIDDEN"})
    
    full_path: bpy.props.StringProperty(options={"HIDDEN"})
    
    db_name: bpy.props.StringProperty(options={"HIDDEN"})
    db_type: bpy.props.StringProperty(options={"HIDDEN"})

    prop_name: bpy.props.StringProperty(options={"HIDDEN"})
    prop_identifier: bpy.props.StringProperty(options={"HIDDEN"})
    prop_type: bpy.props.StringProperty(options={"HIDDEN"})
    prop_subtype: bpy.props.StringProperty(options={"HIDDEN"})
    prop_size: bpy.props.IntProperty(options={"HIDDEN"})
    prop_enum_items: bpy.props.StringProperty(options={"HIDDEN"})
    prop_is_enum_set: bpy.props.BoolProperty(default=False,options={"HIDDEN","SKIP_SAVE"})
    node_uid: bpy.props.StringProperty(options={"HIDDEN"})
    node_index: bpy.props.IntProperty(options={"HIDDEN"})
    
    
    def copy(self,data):
        bpy.context.window_manager.clipboard = data


    def construct(self, db_name, db_type, group_path):
        if self.prop_name == "Scripting Property Index":
            addon_tree = bpy.context.scene.sn.addon_tree()
            prop = addon_tree.sn_properties[addon_tree.sn_property_index]
            return construct_from_attached_property(prop.attach_property_to, prop.attach_property_to, prop)

        elif self.prop_name == "Operator Property Index":
            for graph in bpy.context.scene.sn.addon_tree().sn_graphs:
                for node in graph.node_tree.nodes:
                    if not node.bl_idname in ["NodeFrame","NodeReroute"] and node.uid == self.node_uid:
                        return construct_from_property("self", node.properties[self.node_index], self.node_uid)

        elif self.prop_name == "Preferences Property Index":
            for graph in bpy.context.scene.sn.addon_tree().sn_graphs:
                for node in graph.node_tree.nodes:
                    if not node.bl_idname in ["NodeFrame","NodeReroute"] and node.uid == self.node_uid:
                        return construct_from_property("context.preferences.addons[__name__.partition('.')[0]].preferences", node.properties[self.node_index], self.node_uid)

        else:
            data = {
                "data_block": {
                    "name": db_name,
                    "type": db_type
                },
                "group_path": group_path,
                "property": {
                    "name": self.prop_name,
                    "identifier": self.prop_identifier,
                    "type": self.prop_type,
                    "subtype": self.prop_subtype,
                    "size": self.prop_size,
                    "items": self.prop_enum_items,
                    "is_set": self.prop_is_enum_set,
                    "created_from": "NONE",
                    "removed": False
                }
            }
            return json.dumps(data)
    
    
    def space_data(self):
        group_path = "spaces[0]" + self.full_path.split("]")[-1]
        return self.construct("Area","Area",group_path)
    
    
    def space(self):
        return self.construct("Area","Area","spaces[0]")


    def preferences(self):
        return self.construct(self.db_name + " Preferences",self.db_type,"")
                        
        
    def default(self):
        db_type = self.db_type
        db_name = self.db_name
        group_path = self.full_path.split("]")[-1][1:]
        if not self.full_path[-1] == "]":
            db = eval("]".join(self.full_path.split("]")[:-1])+"]")
            db_name = db.name
            db_type = db.bl_rna.identifier
        return self.construct(db_name,db_type,group_path)


    def execute(self, context):
        if self.origin == "SPACE_DATA":
            self.copy(self.space_data())
        elif self.origin == "SPACE":
            self.copy(self.space())
        elif self.origin == "PREFERENCES":
            self.copy(self.preferences())
        elif self.origin == "DEFAULT":
            self.copy(self.default())
        return {"FINISHED"}




class WM_MT_button_context(bpy.types.Menu):
    bl_label = "Unused"

    def draw(self, context):
        pass
    


def serpens_right_click(self, context):
    layout = self.layout

    property_pointer = getattr(context, "button_pointer", None)
    property_value = getattr(context, "button_prop", None)
    button_value = getattr(context, "button_operator", None)    

    if property_value or button_value:
        layout.separator()
        
    # print(property_pointer, property_value, button_value, property_value.identifier)
    # print(context.blend_data.id_data)
    
    # if property_pointer and property_value:
    #     print(property_pointer.path_resolve(property_value.identifier, False).__repr__())
    
    if property_value and property_pointer:
        op = layout.operator("sn.copy_space_property",text="Serpens | Copy Property",icon="COPYDOWN")

        if "Preferences" in property_pointer.bl_rna.identifier:
            op.origin = "PREFERENCES"
        elif property_pointer.bl_rna.identifier in ["SpaceView3D"]:
            op.origin = "SPACE"
        elif "bpy.data.screens[" in property_pointer.__repr__():
            op.origin = "SPACE_DATA"
        else:
            op.origin = "DEFAULT"
        
        if "ObjectBase" in property_pointer.__repr__():
            op.full_path = "bpy.data.objects[\"My Object\"]"
            op.db_type = "Object"
            op.db_name = "Object"

        else:
            op.full_path = property_pointer.__repr__()
            op.db_type = property_pointer.bl_rna.identifier
            op.db_name = property_pointer.bl_rna.name
        
        if hasattr(property_pointer, f'["{property_value.identifier}"]'):
            op.prop_identifier = f'["{property_value.identifier}"]'
        else:
            op.prop_identifier = property_value.identifier
        
        op.prop_name = property_value.name
        op.prop_type = property_value.type
        op.prop_subtype = property_value.subtype
        if property_value.name in ["Operator Property Index", "Preferences Property Index"]:
            op.node_uid = property_pointer.uid
            op.node_index = property_pointer.property_index

        if hasattr(property_value,"array_length"):
            op.prop_size = property_value.array_length
        else:
            op.prop_size = -1
            
        if hasattr(property_value,"enum_items"):
            items = "["
            for item in property_value.enum_items:
                items += f"(\"{item.identifier}\",\"{item.name}\",\"{item.description}\"),"
            op.prop_enum_items = items + "]"
            op.prop_is_enum_set = property_value.is_enum_flag
            
    else:
        if bpy.ops.ui.copy_python_command_button.poll():
            layout.operator("ui.copy_python_command_button",text="Serpens | Copy Operator",icon="COPYDOWN")
        else:
            layout.label(text="You can't copy operators out of floating menus")