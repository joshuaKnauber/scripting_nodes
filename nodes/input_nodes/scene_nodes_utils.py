import bpy

def add_data_output(self,prop,label,prop_type=""):
    if prop:
        prop_type = str(type(prop))
    if prop_type == str(str) or prop_type in [str(bpy.types.StringProperty),str(bpy.types.EnumProperty)]:
        out = self.outputs.new('SN_StringSocket', label)
    elif prop_type == str(bool) or prop_type == str(bpy.types.BoolProperty):
        out = self.outputs.new('SN_BooleanSocket', label)
    elif prop_type == str(tuple):# or prop_type in [str(bpy.types.FloatVectorProperty)]:
        out = self.outputs.new('SN_VectorSocket', label)
    elif prop_type in [str(int),str(float)] or prop_type in [str(bpy.types.FloatProperty),str(bpy.types.IntProperty)]:
        out = self.outputs.new('SN_NumberSocket', label)
    else:
        out = self.outputs.new('SN_SceneDataSocket', label)
        out.display_shape = "SQUARE"

def get_bpy_types():
    return {
        "cameras": "Camera",
        "scenes": "Scene",
        "objects": "Object",
        "materials": "Material",
        "node_groups": "NodeGroup",
        "meshes": "Mesh",
        "lights": "Light",
        "libraries": "Library",
        "screens": "Screen",
        "window_managers": "WindowManager",
        "images": "Image",
        "lattices": "Lattice",
        "curves": "Curve",
        "metaballs": "MetaBall",
        "fonts": "Font",
        "textures": "Texture",
        "brushes": "Brush",
        "worlds": "World",
        "collections": "Collection",
        "shape_keys": "ShapeKey",
        "texts": "Text",
        "speakers": "Speaker",
        "sounds": "Sound",
        "armatures": "Armature",
        "actions": "Action",
        "particles": "Particle",
        "palettes": "Palette",
        "grease_pencils": "GreasePencil",
        "movieclips": "MovieClip",
        "masks": "Mask",
        #"linestyles": "BlendDataLineStyles",
        "cache_files": "CacheFile",
        "paint_curves": "PaintCurve",
        "workspaces": "WorkSpace",
        "lightprobes": "LightProbe",
        "volumes": "Volume",
    }

def get_active_types():
    return {
        "objects": "object",
        "materials": "material"
    }


class SN_OT_AddSceneDataSocket(bpy.types.Operator):
    bl_idname = "scripting_nodes.add_scene_data_socket"
    bl_label = "Add output"
    bl_description = "Adds the selected output"
    bl_options = {"REGISTER","INTERNAL"}

    node_name: bpy.props.StringProperty()
    socket_name: bpy.props.StringProperty()

    def execute(self, context):
        for node in context.space_data.node_tree.nodes:
            if node.name == self.node_name:
                for prop in node.search_properties:
                    if prop.name == self.socket_name:
                        add_data_output(node,None,self.socket_name,prop.propType)
        return {"FINISHED"}


class SN_OT_RemoveSceneDataSocket(bpy.types.Operator):
    bl_idname = "scripting_nodes.remove_scene_data_socket"
    bl_label = "Remove output"
    bl_description = "Removes the selected output"
    bl_options = {"REGISTER","INTERNAL"}

    node_name: bpy.props.StringProperty()
    socket_name: bpy.props.StringProperty()

    def execute(self, context):
        for node in context.space_data.node_tree.nodes:
            if node.name == self.node_name:
                for output in node.outputs:
                    if output.name == self.socket_name:
                        node.outputs.remove(output)
        return {"FINISHED"}