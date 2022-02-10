import bpy



def is_valid_attribute(attr):
    return not attr in ["rna_type", "original", "bl_rna"] and not attr[0] == "_"
    


class SN_DataProperty(bpy.types.PropertyGroup):
    
    def update_expand(self, context):
        if not self.items_added and self.has_properties:
            context.scene.sn.create_data_items(eval(self.path), self.path)
            self.items_added = True


    name: bpy.props.StringProperty()

    identifier: bpy.props.StringProperty()

    description: bpy.props.StringProperty()

    type: bpy.props.StringProperty()

    path: bpy.props.StringProperty()

    parent_path: bpy.props.StringProperty()
    
        
    has_properties: bpy.props.BoolProperty()
    
    items_added: bpy.props.BoolProperty(default=False)
    
    expand: bpy.props.BoolProperty(default=False,
                                update=update_expand,
                                name="Expand",
                                description="Expand the items of this property")