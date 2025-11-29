from scripting_nodes.src.features.nodes.categories.Blend_Data.blend_data_base_node import BlendDataBaseNode
import bpy

class SNA_Node_BlendDataMaterials(BlendDataBaseNode, bpy.types.Node):

    bl_idname = "SNA_BlendDataMaterials"
    bl_label = "Materials"

    data_type = "Material"
    data_type_plural = "Materials"
    
    active_path = "bpy.context.object.active_material"
    data_path = "bpy.data.materials"



class SNA_Node_BlendDataMetaballs(BlendDataBaseNode, bpy.types.Node):

    bl_idname = "SNA_BlendDataMetaballs"
    bl_label = "Metaballs"

    data_type = "Metaball"
    data_type_plural = "Metaballs"
    
    data_path = "bpy.data.metaballs"



class SNA_Node_BlendDataCurves(BlendDataBaseNode, bpy.types.Node):

    bl_idname = "SNA_BlendDataCurves"
    bl_label = "Curves"

    data_type = "Curve"
    data_type_plural = "Curves"
    
    data_path = "bpy.data.curves"



class SNA_Node_BlendDataActions(BlendDataBaseNode, bpy.types.Node):

    bl_idname = "SNA_BlendDataActions"
    bl_label = "Actions"

    data_type = "Action"
    data_type_plural = "Actions"
    
    data_path = "bpy.data.actions"



class SNA_Node_BlendDataArmatures(BlendDataBaseNode, bpy.types.Node):

    bl_idname = "SNA_BlendDataArmatures"
    bl_label = "Armatures"

    data_type = "Armature"
    data_type_plural = "Armatures"
    
    data_path = "bpy.data.armatures"



class SNA_Node_BlendDataImages(BlendDataBaseNode, bpy.types.Node):

    bl_idname = "SNA_BlendDataImages"
    bl_label = "Images"

    data_type = "Image"
    data_type_plural = "Images"
    
    data_path = "bpy.data.images"



class SNA_Node_BlendDataLights(BlendDataBaseNode, bpy.types.Node):

    bl_idname = "SNA_BlendDataLights"
    bl_label = "Lights"

    data_type = "Light"
    data_type_plural = "Lights"
    
    data_path = "bpy.data.lights"



class SNA_Node_BlendDataNodeGroups(BlendDataBaseNode, bpy.types.Node):

    bl_idname = "SNA_BlendDataNodeGroups"
    bl_label = "Node Groups"

    data_type = "Node Group"
    data_type_plural = "Node Groups"
    
    data_path = "bpy.data.node_groups"



class SNA_Node_BlendDataTexts(BlendDataBaseNode, bpy.types.Node):

    bl_idname = "SNA_BlendDataTexts"
    bl_label = "Texts"

    data_type = "Text"
    data_type_plural = "Texts"
    
    data_path = "bpy.data.texts"



class SNA_Node_BlendDataTextures(BlendDataBaseNode, bpy.types.Node):

    bl_idname = "SNA_BlendDataTextures"
    bl_label = "Textures"

    data_type = "Texture"
    data_type_plural = "Textures"
    
    data_path = "bpy.data.textures"



class SNA_Node_BlendDataWorkspaces(BlendDataBaseNode, bpy.types.Node):

    bl_idname = "SNA_BlendDataWorkspaces"
    bl_label = "Workspaces"

    data_type = "Workspace"
    data_type_plural = "Workspaces"
    
    data_path = "bpy.data.workspaces"
    active_path = "bpy.context.workspace"



class SNA_Node_BlendDataWorlds(BlendDataBaseNode, bpy.types.Node):

    bl_idname = "SNA_BlendDataWorlds"
    bl_label = "Worlds"

    data_type = "World"
    data_type_plural = "Worlds"
    
    data_path = "bpy.data.worlds"
    active_path = "bpy.context.scene.world"



class SNA_Node_BlendDataBrushes(BlendDataBaseNode, bpy.types.Node):

    bl_idname = "SNA_BlendDataBrushes"
    bl_label = "Brushes"

    data_type = "Brush"
    data_type_plural = "Brushes"
    
    data_path = "bpy.data.brushes"



class SNA_Node_BlendDataCameras(BlendDataBaseNode, bpy.types.Node):

    bl_idname = "SNA_BlendDataCameras"
    bl_label = "Cameras"

    data_type = "Camera"
    data_type_plural = "Cameras"
    
    data_path = "bpy.data.cameras"
    active_path = "bpy.context.scene.camera.data"



class SNA_Node_BlendDataFonts(BlendDataBaseNode, bpy.types.Node):

    bl_idname = "SNA_BlendDataFonts"
    bl_label = "Fonts"

    data_type = "Font"
    data_type_plural = "Fonts"
    
    data_path = "bpy.data.fonts"



class SNA_Node_BlendDataGreasePencils(BlendDataBaseNode, bpy.types.Node):

    bl_idname = "SNA_BlendDataGreasePencils"
    bl_label = "Grease Pencils"

    data_type = "Grease Pencil"
    data_type_plural = "Grease Pencils"
    
    data_path = "bpy.data.grease_pencils"



class SNA_Node_BlendDataLattices(BlendDataBaseNode, bpy.types.Node):

    bl_idname = "SNA_BlendDataLattices"
    bl_label = "Lattices"

    data_type = "Lattice"
    data_type_plural = "Lattices"
    
    data_path = "bpy.data.lattices"



class SNA_Node_BlendDataScenes(BlendDataBaseNode, bpy.types.Node):

    bl_idname = "SNA_BlendDataScenes"
    bl_label = "Scenes"

    data_type = "Scene"
    data_type_plural = "Scenes"
    
    data_path = "bpy.data.scenes"
    active_path = "bpy.context.scene"



class SNA_Node_BlendDataScreens(BlendDataBaseNode, bpy.types.Node):

    bl_idname = "SNA_BlendDataScreens"
    bl_label = "Screens"

    data_type = "Screen"
    data_type_plural = "Screens"
    
    data_path = "bpy.data.screens"
    active_path = "bpy.context.screen"



class SNA_Node_BlendDataShapeKeys(BlendDataBaseNode, bpy.types.Node):

    bl_idname = "SNA_BlendDataShapeKeys"
    bl_label = "Shape Keys"

    data_type = "Shape Key"
    data_type_plural = "Shape Keys"
    
    data_path = "bpy.data.shape_keys"



class SNA_Node_BlendDataVolumes(BlendDataBaseNode, bpy.types.Node):

    bl_idname = "SNA_BlendDataVolumes"
    bl_label = "Volumes"

    data_type = "Volume"
    data_type_plural = "Volumes"
    
    data_path = "bpy.data.volumes"



class SNA_Node_BlendDataWindowManagers(BlendDataBaseNode, bpy.types.Node):

    bl_idname = "SNA_BlendDataWindowManagers"
    bl_label = "Window Managers"

    data_type = "Window Manager"
    data_type_plural = "Window Managers"
    
    data_path = "bpy.data.window_managers"
    active_path = "bpy.context.window_manager"