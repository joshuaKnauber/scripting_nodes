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
    "Pointer": "MONKEY",
    "Property": "MONKEY",
    "Collection": "ASSET_MANAGER",
    "Collection Property": "ASSET_MANAGER",
    "Group": "FILEBROWSER",
    "List": "LONGDISPLAY",
    "Data": "OBJECT_DATA",
    "Icon": "DRIVER_TRANSFORM",
}



_prop_cache = {} # stores key, value of settings.as_pointer with prop for settings

class PropertySettings:
    
    dummy: bpy.props.StringProperty(name="DUMMY", description="Dummy prop for resolving path")
    
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