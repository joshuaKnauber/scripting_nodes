import bpy
from ..base_node import SN_ScriptingBaseNode
from .blend_data_base import BlendDataBaseNode



class SN_MaterialsBlendDataNode(bpy.types.Node, BlendDataBaseNode, SN_ScriptingBaseNode):

    bl_idname = "SN_MaterialsBlendDataNode"
    bl_label = "Materials"

    data_type = "Material"
    data_type_plural = "Materials"
    
    active_path = "bpy.context.object.active_material"
    data_path = "bpy.data.materials"



class SN_MetaballsBlendDataNode(bpy.types.Node, BlendDataBaseNode, SN_ScriptingBaseNode):

    bl_idname = "SN_MetaballsBlendDataNode"
    bl_label = "Metaballs"

    data_type = "Metaball"
    data_type_plural = "Metaballs"
    
    data_path = "bpy.data.metaballs"



class SN_CurvesBlendDataNode(bpy.types.Node, BlendDataBaseNode, SN_ScriptingBaseNode):

    bl_idname = "SN_CurvesBlendDataNode"
    bl_label = "Curves"

    data_type = "Curve"
    data_type_plural = "Curves"
    
    data_path = "bpy.data.curves"



class SN_ActionsBlendDataNode(bpy.types.Node, BlendDataBaseNode, SN_ScriptingBaseNode):

    bl_idname = "SN_ActionsBlendDataNode"
    bl_label = "Actions"

    data_type = "Action"
    data_type_plural = "Actions"
    
    data_path = "bpy.data.actions"



class SN_ArmaturesBlendDataNode(bpy.types.Node, BlendDataBaseNode, SN_ScriptingBaseNode):

    bl_idname = "SN_ArmaturesBlendDataNode"
    bl_label = "Armatures"

    data_type = "Armature"
    data_type_plural = "Armatures"
    
    data_path = "bpy.data.armatures"



class SN_ImagesBlendDataNode(bpy.types.Node, BlendDataBaseNode, SN_ScriptingBaseNode):

    bl_idname = "SN_ImagesBlendDataNode"
    bl_label = "Images"

    data_type = "Image"
    data_type_plural = "Images"
    
    data_path = "bpy.data.images"



class SN_LightsBlendDataNode(bpy.types.Node, BlendDataBaseNode, SN_ScriptingBaseNode):

    bl_idname = "SN_LightsBlendDataNode"
    bl_label = "Lights"

    data_type = "Light"
    data_type_plural = "Lights"
    
    data_path = "bpy.data.lights"



class SN_NodeGroupsBlendDataNode(bpy.types.Node, BlendDataBaseNode, SN_ScriptingBaseNode):

    bl_idname = "SN_NodeGroupsBlendDataNode"
    bl_label = "Node Groups"

    data_type = "Node Group"
    data_type_plural = "Node Groups"
    
    data_path = "bpy.data.node_groups"



class SN_TextsBlendDataNode(bpy.types.Node, BlendDataBaseNode, SN_ScriptingBaseNode):

    bl_idname = "SN_TextsBlendDataNode"
    bl_label = "Texts"

    data_type = "Text"
    data_type_plural = "Texts"
    
    data_path = "bpy.data.texts"



class SN_TexturesBlendDataNode(bpy.types.Node, BlendDataBaseNode, SN_ScriptingBaseNode):

    bl_idname = "SN_TexturesBlendDataNode"
    bl_label = "Textures"

    data_type = "Texture"
    data_type_plural = "Textures"
    
    data_path = "bpy.data.textures"



class SN_WorkspacesBlendDataNode(bpy.types.Node, BlendDataBaseNode, SN_ScriptingBaseNode):

    bl_idname = "SN_WorkspacesBlendDataNode"
    bl_label = "Workspaces"

    data_type = "Workspace"
    data_type_plural = "Workspaces"
    
    data_path = "bpy.data.workspaces"
    active_path = "bpy.context.workspace"



class SN_WorldsBlendDataNode(bpy.types.Node, BlendDataBaseNode, SN_ScriptingBaseNode):

    bl_idname = "SN_WorldsBlendDataNode"
    bl_label = "Worlds"

    data_type = "World"
    data_type_plural = "Worlds"
    
    data_path = "bpy.data.worlds"
    active_path = "bpy.context.scene.world"



class SN_BrushesBlendDataNode(bpy.types.Node, BlendDataBaseNode, SN_ScriptingBaseNode):

    bl_idname = "SN_BrushesBlendDataNode"
    bl_label = "Brushes"

    data_type = "Brush"
    data_type_plural = "Brushes"
    
    data_path = "bpy.data.brushes"



class SN_CamerasBlendDataNode(bpy.types.Node, BlendDataBaseNode, SN_ScriptingBaseNode):

    bl_idname = "SN_CamerasBlendDataNode"
    bl_label = "Cameras"

    data_type = "Camera"
    data_type_plural = "Cameras"
    
    data_path = "bpy.data.cameras"
    active_path = "bpy.context.scene.camera"



class SN_FontsBlendDataNode(bpy.types.Node, BlendDataBaseNode, SN_ScriptingBaseNode):

    bl_idname = "SN_FontsBlendDataNode"
    bl_label = "Fonts"

    data_type = "Font"
    data_type_plural = "Fonts"
    
    data_path = "bpy.data.fonts"



class SN_GreasePencilsBlendDataNode(bpy.types.Node, BlendDataBaseNode, SN_ScriptingBaseNode):

    bl_idname = "SN_GreasePencilsBlendDataNode"
    bl_label = "Grease Pencils"

    data_type = "Grease Pencil"
    data_type_plural = "Grease Pencils"
    
    data_path = "bpy.data.grease_pencils"



class SN_LatticesBlendDataNode(bpy.types.Node, BlendDataBaseNode, SN_ScriptingBaseNode):

    bl_idname = "SN_LatticesBlendDataNode"
    bl_label = "Lattices"

    data_type = "Lattice"
    data_type_plural = "Lattices"
    
    data_path = "bpy.data.lattices"



class SN_ScenesBlendDataNode(bpy.types.Node, BlendDataBaseNode, SN_ScriptingBaseNode):

    bl_idname = "SN_ScenesBlendDataNode"
    bl_label = "Scenes"

    data_type = "Scene"
    data_type_plural = "Scenes"
    
    data_path = "bpy.data.scenes"
    active_path = "bpy.context.scene"



class SN_ScreensBlendDataNode(bpy.types.Node, BlendDataBaseNode, SN_ScriptingBaseNode):

    bl_idname = "SN_ScreensBlendDataNode"
    bl_label = "Screens"

    data_type = "Screen"
    data_type_plural = "Screens"
    
    data_path = "bpy.data.screens"
    active_path = "bpy.context.screen"



class SN_ShapeKeysBlendDataNode(bpy.types.Node, BlendDataBaseNode, SN_ScriptingBaseNode):

    bl_idname = "SN_ShapeKeysBlendDataNode"
    bl_label = "Shape Keys"

    data_type = "Shape Key"
    data_type_plural = "Shape Keys"
    
    data_path = "bpy.data.shape_keys"



class SN_VolumesBlendDataNode(bpy.types.Node, BlendDataBaseNode, SN_ScriptingBaseNode):

    bl_idname = "SN_VolumesBlendDataNode"
    bl_label = "Volumes"

    data_type = "Volume"
    data_type_plural = "Volumes"
    
    data_path = "bpy.data.volumes"



class SN_WindowManagersBlendDataNode(bpy.types.Node, BlendDataBaseNode, SN_ScriptingBaseNode):

    bl_idname = "SN_WindowManagersBlendDataNode"
    bl_label = "Window Managers"

    data_type = "Window Manager"
    data_type_plural = "Window Managers"
    
    data_path = "bpy.data.window_managers"
    active_path = "bpy.context.window_manager"