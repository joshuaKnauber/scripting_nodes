import bpy
from ...addon.properties.property_basic import BasicProperty
from ...addon.properties.property_utils import get_sorted_props



class SN_NodeProperty(BasicProperty, bpy.types.PropertyGroup):
    
    @property
    def data_path(self):
        data = self.prop_collection_origin.bl_label.replace(" ", "_").upper() + "_PLACEHOLDER"
        return f"{data}.{self.python_name}"
    
    
    @property
    def register_code_imperative(self):
        # create property groups
        if self.property_type == "Group" and hasattr(self, "imperative_code"):
            return self.settings.imperative_code()
        return ""
    
    
    @property
    def register_code(self):
        # register group properties
        if self.property_type == "Group":
            return f"bpy.utils.register_class(SNA_GROUP_{self.python_name})"
        return ""
    
    
    @property
    def register_code_props(self):
        # register non group properties
        if not self.property_type == "Group":
            code = f"{self.python_name}: bpy.props.{self.settings.prop_type_name}(name='{self.name}', description='{self.description}', {self.settings.register_options})"
            # add register code from prop settings
            if hasattr(self.settings, "imperative_code"):
                return self.settings.imperative_code() + "\n" + code
            return code
        return ""
    
    
    @property
    def unregister_code(self):
        # unregister group properties
        if self.property_type == "Group":
            return f"bpy.utils.unregister_class(SNA_GROUP_{self.python_name})"
        return ""
    
    
    def compile(self, context=None):
        self.prop_collection_origin._evaluate(bpy.context)



class PropertyNode():
    
    property_index: bpy.props.IntProperty(name="Index",
                                description="Index of the selected property",
                                min=0, default=0)

    properties: bpy.props.CollectionProperty(type=SN_NodeProperty)
    
    
    def props_imperative(self, context):
        code = ""
        props = get_sorted_props(self.properties.values())
        for prop in props:
            code += prop.register_code_imperative + "\n"
        return code
    

    def props_register(self, context):
        code = ""
        props = get_sorted_props(self.properties.values())
        for prop in props:
            code += prop.register_code + "\n"
        return code
    

    def props_unregister(self, context):
        code = ""
        props = get_sorted_props(self.properties.values())
        props.reverse()
        for prop in props:
            code += prop.unregister_code + "\n"
        return code
    

    def props_code(self, context):
        code = ""
        props = get_sorted_props(self.properties.values())
        for prop in props:
            code += prop.register_code_props + "\n"
        return code
    

    def draw_list(self, layout):
        row = layout.row()
        row.template_list("SN_UL_PropertyList", "", self, "properties", self, "property_index")

        col = row.column(align=True)
        op = col.operator("sn.edit_node_property", text="", icon="GREASEPENCIL")
        op.node_tree = self.node_tree.name
        op.node = self.name
        col.separator()

        op = col.operator("sn.add_node_property", text="", icon="ADD")
        op.node_tree = self.node_tree.name
        op.node = self.name
        op = col.operator("sn.remove_node_property", text="", icon="REMOVE")
        op.node_tree = self.node_tree.name
        op.node = self.name

        col.separator()
        subrow = col.row(align=True)
        subrow.enabled = self.property_index > 0
        op = subrow.operator("sn.move_node_property", text="", icon="TRIA_UP")
        op.node_tree = self.node_tree.name
        op.node = self.name
        op.move_up = True
        subrow = col.row(align=True)
        subrow.enabled = self.property_index < len(self.properties)-1
        op = subrow.operator("sn.move_node_property", text="", icon="TRIA_DOWN")
        op.node_tree = self.node_tree.name
        op.node = self.name
        op.move_up = False