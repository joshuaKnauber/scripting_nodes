import bpy
from ....utils import normalize_code
from .settings import PropertySettings



class EnumItem(bpy.types.PropertyGroup):
    
    name: bpy.props.StringProperty(name="Name", default="New Item",
                                description="Name of this enum item")
    
    description: bpy.props.StringProperty(name="Description",
                                description="Description of this enum item")
    
    icon: bpy.props.IntProperty(name="Icon", default=0, min=0,
                                description="Icon value of this enum item")




class SN_PT_EnumProperty(PropertySettings, bpy.types.PropertyGroup):
    
    type_description = "Enum properties can hold a multiple items with a name and description.\n" \
                    + "\n" \
                    + "Enum properties are displayed as dropdowns or a list of toggles.\n" \
                    + "Dynamic enums can be used to display custom icons such as a list of asset images."
                    
    
    def draw(self, context, layout, prop):
        """ Draws the settings for this property type """
        layout.prop(self, "enum_flag")
        layout.prop(self, "is_dynamic")

        if not self.is_dynamic:
            layout.separator()
            row = layout.row()
            row.scale_y = 1.2
            op = row.operator("sn.add_enum_item", text="Add Item", icon="ADD")
            op.item_data_path = "context.scene.sn.properties[context.scene.sn.property_index].settings.items"

            for i, item in enumerate(self.items):
                box = layout.box()
                box.use_property_split = False
                row = box.row()
                row.prop(item, "name")
                op = row.operator("sn.select_icon", icon_value=item.icon if item.icon != 0 else 101, text="", emboss=item.icon==0)
                op.icon_data_path = f"context.scene.sn.properties[context.scene.sn.property_index].settings.items[{i}]"
                box.prop(item, "description")
        
    
    @property
    def prop_type_name(self):
        return "EnumProperty"
    
    
    @property
    def register_options(self):
        options = ""
        if not self.is_dynamic:
            items = [f"('{item.name}', '{item.name}', '{item.description}', {item.icon}, {i})" for i, item in enumerate(self.items)]
            options = f"items=[{', '.join(items)}]"
        else:
            options = f"items={f'{self.prop.python_name}_enum_items'}"
            
        if self.enum_flag:
            options += ", options={'ENUM_FLAG'}" # TODO you can't select the first item when this is enabled
        return options
    
    
    def register_code(self, code):
        # TODO this wont work inside of operators, preferences or on export
        # TODO this is different on export
        code = f"""
                def {self.prop.python_name}_enum_items(self, context):
                    for ntree in bpy.data.node_groups:
                        if ntree.bl_idname == "ScriptingNodesTree":
                            for node in ntree.nodes:
                                if node.bl_idname == "SN_GenerateEnumItemsNode" and node.prop_name == "{self.prop.name}":
                                    items = eval(node.code)
                                    return [node.make_enum_item(item[0], item[1], item[2], item[3], item[4]) for item in items]
                    return [("No Items", "No Items", "No generate enum items node found to create items!", "ERROR", 0)]
                {code}
                """
        return normalize_code(code)
    
    
    enum_flag: bpy.props.BoolProperty(name="Select Multiple",
                                description="Lets you select multiple options from this property",
                                update=PropertySettings.compile)
    
    
    is_dynamic: bpy.props.BoolProperty(name="Dynamic Items",
                                description="The items are generated with a function and aren't predefined",
                                update=PropertySettings.compile)
    
    
    items: bpy.props.CollectionProperty(type=EnumItem,
                                name="Items",
                                description="Enum Items")