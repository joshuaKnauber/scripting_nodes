import bpy
from ....utils import normalize_code
from .settings import PropertySettings



_enum_prop_cache = {} # stores key, value of enum.as_pointer, prop

class EnumItem(bpy.types.PropertyGroup):
    
    @property
    def prop(self):
        if self.id_data.bl_rna.identifier == "ScriptingNodesTree":
            # find property in nodes to return
            if not str(self.as_pointer()) in _enum_prop_cache:
                for node in self.id_data.nodes:
                    if hasattr(node, "properties"):
                        for prop in node.properties:
                            if prop.property_type == "Enum":
                                for item in prop.settings.items:
                                    if item == self:
                                        _enum_prop_cache[str(self.as_pointer())] = prop
                                        break
                            elif prop.property_type == "Group":
                                for subprop in prop.settings.properties:
                                    if subprop.property_type == "Enum":
                                        for item in subprop.settings.items:
                                            if item == self:
                                                _enum_prop_cache[str(self.as_pointer())] = prop
                                                break
            return _enum_prop_cache[str(self.as_pointer())]
        
        else:
            path = ".".join(repr(self.path_resolve("name", False)).split(".")[:-2])
            prop = eval(path)
            return prop
    
    def update(self, context):
        self.prop.compile()
        
    name: bpy.props.StringProperty(name="Name", default="New Item",
                                description="Name of this enum item",
                                update=update)
    
    description: bpy.props.StringProperty(name="Description",
                                description="Description of this enum item",
                                update=update)
    
    icon: bpy.props.IntProperty(name="Icon", default=0, min=0,
                                description="Icon value of this enum item",
                                update=update)




class SN_PT_EnumProperty(PropertySettings, bpy.types.PropertyGroup):
    
    type_description = "Enum properties can hold multiple items with a name and description.\n" \
                    + "\n" \
                    + "Enum properties are displayed as dropdowns or a list of toggles.\n" \
                    + "Dynamic enums can be used to display custom icons such as a list of asset images."
                    
    
    def draw(self, context, layout):
        """ Draws the settings for this property type """
        layout.prop(self, "enum_flag")
        layout.prop(self, "is_dynamic")

        layout.separator()
        row = layout.row()
        row.scale_y = 1.2
        if not self.is_dynamic:
            op = row.operator("sn.add_enum_item", text="Add Item", icon="ADD")
            op.item_data_path = f"{self.prop.full_prop_path}.settings.items"

            for i, item in enumerate(self.items):
                box = layout.box()
                col = box.column(align=True)
                box.use_property_split = False
                row = col.row()
                row.prop(item, "name")
                op = row.operator("sn.select_icon", icon_value=item.icon if item.icon != 0 else 101, text="", emboss=item.icon==0)
                op.icon_data_path = f"{self.prop.full_prop_path}.settings.items[{i}]"
                col.prop(item, "description")
                
        else:
            op = row.operator("node.add_node", text="Generate Items", icon="ADD")
            op.type = "SN_GenerateEnumItemsNode"
            op.use_transform = True
        
    
    @property
    def prop_type_name(self):
        return "EnumProperty"
    
    
    @property
    def item_func_name(self):
        name = f"{self.prop.python_name}_enum_items"
        if hasattr(self.prop, "group_prop_parent"):
            return f"{self.prop.group_prop_parent.python_name}_{name}"
        return name
    
    
    @property
    def register_options(self):
        options = ""
        if not self.is_dynamic:
            items = []
            for i, item in enumerate(self.items):
                if self.enum_flag:
                    i = 2 ** i
                items.append(f"('{item.name}', '{item.name}', '{item.description}', {item.icon}, {i})")
            options = f"items=[{', '.join(items)}]"
        else:
            options = f"items={self.item_func_name}"
            
        if self.enum_flag:
            options += ", options={'ENUM_FLAG'}"
        return options + self.update_option
    
    
    def imperative_code(self):
        # node exists for this property
        for ntree in bpy.data.node_groups:
            if ntree.bl_idname == "ScriptingNodesTree":
                for ref in ntree.node_collection("SN_GenerateEnumItemsNode").refs:
                    node = ref.node
                    enum_src = node.get_prop_source()
                    if enum_src and node.prop_name in enum_src.properties and enum_src.properties[node.prop_name] == self.prop:
                        return ""

        code = f"""
            def {self.item_func_name}(self, context):
                return [("No Items", "No Items", "No generate enum items node found to create items!", "ERROR", 0)]
            """
        return normalize_code(code) + "\n" + self.update_function
    
    
    enum_flag: bpy.props.BoolProperty(name="Select Multiple",
                                description="Lets you select multiple options from this property",
                                update=PropertySettings.compile)
    
    
    is_dynamic: bpy.props.BoolProperty(name="Dynamic Items",
                                description="The items are generated with a function and aren't predefined",
                                update=PropertySettings.compile)
    
    
    items: bpy.props.CollectionProperty(type=EnumItem,
                                name="Items",
                                description="Enum Items")