import bpy



id_items = ["Scene", "Action", "Armature", "Brush", "CacheFile", "Camera",
        "Collection", "Curve", "FreestyleLineStyle", "GreasePencil",
        "Image", "Key", "Lattice", "Library", "Light", "LightProbe",
        "Mask", "Material", "Mesh", "MetaBall", "MovieClip", "NodeTree",
        "Object", "PaintCurve", "Palette", "ParticleSettings",
        "Screen", "Sound", "Speaker", "Text", "Texture", "VectorFont",
        "Volume", "WindowManager", "WorkSpace", "World"]

id_data = {"Scene": "scenes", "Action":"actions", "Armature":"armatures",
        "Brush":"bruhes", "CacheFile":"cache_files", "Camera":"cameras",
        "Collection":"collections", "Curve":"curves", "FreestyleLineStyle":"linestyles",
        "GreasePencil":"grease_pencils", "Image": "images", "Key": "shape_keys",
        "Lattice": "lattices", "Library": "libraries", "Light": "lights",
        "LightProbe": "lightprobes", "Mask": "masks", "Material": "materials",
        "Mesh": "meshes", "MetaBall": "metaballs", "MovieClip": "movieclips",
        "NodeTree": "node_groups", "Object": "objects", "PaintCurve": "paint_curves",
        "Palette": "palettes", "ParticleSettings": "particles", "Screen": "screens",
        "Sound": "sounds", "Speaker": "speakers", "Text": "texts", "Texture": "textures",
        "VectorFont": "fonts", "Volume": "volumes", "WindowManager": "window_managers",
        "WorkSpace": "workspaces", "World": "worlds"}



property_icons = {
    "String": "SYNTAX_OFF",
    "Boolean": "FORCE_CHARGE",
    "Boolean Vector": "FORCE_CHARGE",
    "Float": "CON_TRANSLIKE",
    "Float Vector": "CON_TRANSLIKE",
    "Integer": "DRIVER_TRANSFORM",
    "Integer Vector": "DRIVER_TRANSFORM",
    "Enum": "PRESET",
    "Enum Set": "PRESET",
    "Pointer": "MONKEY",
    "Property": "MONKEY",
    "Collection": "ASSET_MANAGER",
    "Collection Property": "ASSET_MANAGER",
    "Group": "FILEBROWSER",
    "List": "LONGDISPLAY",
    "Data": "OBJECT_DATA",
    "Icon": "DRIVER_TRANSFORM",

    "Function": "FILE_SCRIPT",
    "Built In Function": "SCRIPTPLUGINS",
}



property_socket = {
    "String": "String",
    "Boolean": "Boolean",
    "Float": "Float",
    "Integer": "Integer",
    "Enum": "Enum",
    "Pointer": "Property",
    "Collection": "Collection Property",
    "Group": "Data",
}

def prop_to_socket(prop):
    socket_name = property_socket[prop.property_type]
    if getattr(prop.settings, "enum_flag", False):
        socket_name = "Enum Set"
    if getattr(prop.settings, "is_vector", False):
        socket_name += " Vector"
    return socket_name


_prop_cache = {} # stores key, value of settings.as_pointer with prop for settings

class PropertySettings:
    
    dummy: bpy.props.StringProperty(name="DUMMY", description="Dummy prop for resolving path")
    
    copy_attributes = []

    def copy(self, new_settings): pass
    
    @property
    def prop(self):
        """ Returns the property these settings belong to """
        if self.id_data.bl_rna.identifier == "ScriptingNodesTree":
            # find property in nodes to return
            if not str(self.as_pointer()) in _prop_cache:
                for node in self.id_data.nodes:
                    if hasattr(node, "properties"):
                        for prop in node.properties:
                            if prop.settings == self:
                                _prop_cache[str(self.as_pointer())] = prop
                                break
                            elif prop.property_type == "Group":
                                for subprop in prop.settings.properties:
                                    if subprop.settings == self:
                                        _prop_cache[str(self.as_pointer())] = subprop
                                        break
            return _prop_cache[str(self.as_pointer())]
        else:
            path = ".".join(repr(self.path_resolve("dummy", False)).split(".")[:-2])
            prop = eval(path)
            return prop

    def compile(self, context=None):
        """ Compile the property for these settings """
        self.prop.compile()
        
    def imperative_code(self):
        return self.update_function
        
    def _update_function_names(self):
        """ Returns the code for the on property update function """
        updates = []
        for ntree in bpy.data.node_groups:
            if ntree.bl_idname == "ScriptingNodesTree":
                for node in ntree.node_collection("SN_OnPropertyUpdateNode").nodes:
                    prop_src = node.get_prop_source()
                    if prop_src and node.prop_name in prop_src.properties:
                        prop = prop_src.properties[node.prop_name]
                        if prop.name == self.prop.name:
                            updates.append((node.update_func_name(prop), node.order))
        return list(map(lambda item: item[0], sorted(updates, key=lambda i: i[1])))
        
    
    @property
    def update_function(self):
        """ Returns the code for the update function """
        update_names = self._update_function_names()
        if len(update_names) < 2:
            return ""
        else:
            code = f"def sna_update_{self.prop.python_name}(self, context):\n"
            for func in update_names:
                code += " "*4 + f"{func}(self, context)\n"
            return code
        
        
    @property
    def update_option(self):
        """ Returns the code for the update function option """
        update_names = self._update_function_names()
        if len(update_names) == 0 or self.prop.property_type in ["Group", "Collection"]:
            return ""
        elif len(update_names) == 1:
            return f", update={update_names[0]}"
        return f", update=sna_update_{self.prop.python_name}"
        