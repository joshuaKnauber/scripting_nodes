import bpy
from .settings import PropertySettings
from ..property_basic import BasicProperty



_group_prop_cache = {} # stores key, value of prop.as_pointer, prop

class SN_SimpleProperty(BasicProperty, bpy.types.PropertyGroup):
    
    expand: bpy.props.BoolProperty(default=True, name="Expand", description="Expand this property")
    
    @property
    def group_prop_parent(self):
        """ Returns the parent of the property collection this property lives in """
        if self.id_data.bl_rna.identifier == "ScriptingNodesTree":
            # find property in nodes to return
            if not str(self.as_pointer()) in _group_prop_cache:
                for node in self.id_data.nodes:
                    if hasattr(node, "properties"):
                        for prop in node.properties:
                            if prop.property_type == "Group":
                                for subprop in prop.settings.properties:
                                    if subprop == self:
                                        _group_prop_cache[str(self.as_pointer())] = prop
                                        break
            return _group_prop_cache[str(self.as_pointer())]
        
        else:
            coll_path = "[".join(repr(self.path_resolve("name", False)).split("[")[:-1])
            parent_path = coll_path.split("stngs_group")[0][:-1]
            return eval(parent_path)
        
    @property
    def python_name(self):
        return super().python_name[4:] # cut of sna_ for props in prop group (mainly for name prop)

    def compile(self, context=None):
        self.group_prop_parent.compile()



class SN_PT_GroupProperty(PropertySettings, bpy.types.PropertyGroup):
    
    type_description = "Group properties can hold multiple other properties.\n" \
                    + "They are used in combination with a pointer or collection property.\n" \
                    + "Use a property called 'Name' to find properties in a collection.\n" \
                    + "\n" \
                    + "A common use for group properties is to group your addons settings together."
    
    
    def draw(self, context, layout):
        """ Draws the settings for this property type """
        row = layout.row()
        row.scale_y = 1.2
        op = row.operator("sn.add_property_item", text="Add Property", icon="ADD")
        op.group_data_path = f"{self.prop.full_prop_path}"
        
        for i, prop in enumerate(self.properties):
            box = layout.box()
            row = box.row()
            subrow = row.row()
            subrow.prop(prop, "expand", text="", icon="DISCLOSURE_TRI_DOWN" if prop.expand else "DISCLOSURE_TRI_RIGHT", emboss=False)
            row.prop(prop, "name", text="")

            subrow = row.row(align=True)
            subcol = subrow.column(align=True)
            subcol.enabled = i > 0
            op = subcol.operator("sn.move_group_property", text="", icon="TRIA_UP")
            op.group_items_path = f"{self.prop.full_prop_path}.settings.properties"
            op.index = i
            op.move_up = True
            subcol = subrow.column(align=True)
            subcol.enabled = i < len(self.properties)-1
            op = subcol.operator("sn.move_group_property", text="", icon="TRIA_DOWN")
            op.group_items_path = f"{self.prop.full_prop_path}.settings.properties"
            op.index = i
            op.move_up = False

            op = row.operator("sn.remove_group_property", text="", icon="TRASH", emboss=False)
            op.group_items_path = f"{self.prop.full_prop_path}.settings.properties"
            op.index = i
            
            row.operator("sn.copy_python_name", text="", icon="COPYDOWN", emboss=False).name = "PROP_PATH_PLACEHOLDER."+prop.python_name

            if prop.expand:
                prop.draw(context, box)
                box.separator()
                prop.settings.draw(context, box)
        
        
    @property
    def prop_type_name(self):
        return f"SNA_GROUP_{self.prop.python_name}"
    
    
    @property
    def register_options(self):
        return f""
    
    
    def imperative_code(self):
        code = f"class {self.prop_type_name}(bpy.types.PropertyGroup):\n\n"
        for prop in self.properties:
            for line in prop.register_code.split("\n"):
                code += " "*4 + line + "\n"
            code += "\n"
        if not len(self.properties):
            code += " "*4 + "pass\n\n"
        return code
    
    
    properties: bpy.props.CollectionProperty(type=SN_SimpleProperty)