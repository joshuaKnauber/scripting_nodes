import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode
from .base_scene_data import SN_SceneDataBase



class SN_ObjectsNode(bpy.types.Node, SN_SceneDataBase, SN_ScriptingBaseNode):

    bl_idname = "SN_ObjectsNode"
    bl_label = "Objects"
    
    data_type = "Object"
    data_identifier = "objects"
    
    active_data = "bpy.context.active_object"
    
    
    
class SN_ActionsNode(bpy.types.Node, SN_SceneDataBase, SN_ScriptingBaseNode):

    bl_idname = "SN_ActionsNode"
    bl_label = "Actions"
    
    data_type = "Action"
    data_identifier = "actions"
    
    
    
class SN_ArmaturesNode(bpy.types.Node, SN_SceneDataBase, SN_ScriptingBaseNode):

    bl_idname = "SN_ArmaturesNode"
    bl_label = "Armatures"
    
    data_type = "Armature"
    data_identifier = "armatures"
    
    
    
class SN_CollectionsNode(bpy.types.Node, SN_SceneDataBase, SN_ScriptingBaseNode):

    bl_idname = "SN_CollectionsNode"
    bl_label = "Collections"
    
    data_type = "Collection"
    data_identifier = "collections"
    
    active_data = "bpy.context.scene.collection"
    
    
    
class SN_ImagesNode(bpy.types.Node, SN_SceneDataBase, SN_ScriptingBaseNode):

    bl_idname = "SN_ImagesNode"
    bl_label = "Images"
    
    data_type = "Image"
    data_identifier = "images"
    
    
    
class SN_LightsNode(bpy.types.Node, SN_SceneDataBase, SN_ScriptingBaseNode):

    bl_idname = "SN_LightsNode"
    bl_label = "Lights"
    
    data_type = "Light"
    data_identifier = "lights"
    
    
    
class SN_MaterialsNode(bpy.types.Node, SN_SceneDataBase, SN_ScriptingBaseNode):

    bl_idname = "SN_MaterialsNode"
    bl_label = "Materials"
    
    data_type = "Material"
    data_identifier = "materials"
    
    
    
class SN_MeshesNode(bpy.types.Node, SN_SceneDataBase, SN_ScriptingBaseNode):

    bl_idname = "SN_MeshesNode"
    bl_label = "Meshes"
    
    data_type = "Mesh"
    data_identifier = "meshes"
    
    active_data = "bpy.context.active_object.data"
    
    
    
class SN_NodeGroupsNode(bpy.types.Node, SN_SceneDataBase, SN_ScriptingBaseNode):

    bl_idname = "SN_NodeGroupsNode"
    bl_label = "Node Groups"
    
    data_type = "NodeTree"
    data_identifier = "node_groups"
    
    
    
class SN_TextsNode(bpy.types.Node, SN_SceneDataBase, SN_ScriptingBaseNode):

    bl_idname = "SN_TextsNode"
    bl_label = "Texts"
    
    data_type = "Text"
    data_identifier = "texts"
    
    
    
class SN_TexturesNode(bpy.types.Node, SN_SceneDataBase, SN_ScriptingBaseNode):

    bl_idname = "SN_TexturesNode"
    bl_label = "Textures"
    
    data_type = "Texture"
    data_identifier = "textures"
    
    
    
class SN_WorkspacesNode(bpy.types.Node, SN_SceneDataBase, SN_ScriptingBaseNode):

    bl_idname = "SN_WorkspacesNode"
    bl_label = "Workspaces"
    
    data_type = "Workspace"
    data_identifier = "workspaces"
    data_identifier = "textures"
    
    active_data = "bpy.context.workspace"
    
    
    
class SN_WorldsNode(bpy.types.Node, SN_SceneDataBase, SN_ScriptingBaseNode):

    bl_idname = "SN_WorldsNode"
    bl_label = "Worlds"
    
    data_type = "World"
    data_identifier = "worlds"
    
    active_data = "bpy.context.scene.world"