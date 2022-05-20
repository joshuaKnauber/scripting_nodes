import bpy
from ..base_node import SN_ScriptingBaseNode



class NodeType(bpy.types.PropertyGroup):
    
    name: bpy.props.StringProperty()
    
    identifier: bpy.props.StringProperty()



class SN_NodeIdnameNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_NodeIdnameNode"
    bl_label = "Node Idname"
    node_color = "STRING"

    def on_create(self, context):
        self.add_string_output("Idname")
       
        # load internal nodes
        for name in dir(bpy.types):
            cls = getattr(bpy.types, name)
            if hasattr(cls, "bl_rna") and cls.bl_rna.base and "Node" in cls.bl_rna.base.bl_rna.name:
                item = self.nodes.add()
                item.name = f"{cls.bl_rna.name} ({cls.bl_rna.base.bl_rna.name})"
                item.identifier = cls.bl_rna.identifier
                
        # load python nodes
        for cls in bpy.types.Node.__subclasses__():
            item = self.nodes.add()
            item.name = f"{cls.bl_rna.name} (Python)"
            item.identifier = cls.bl_rna.identifier
        
        
    nodes: bpy.props.CollectionProperty(type=NodeType)
        
    node: bpy.props.StringProperty(name="Node",
                            description="The node to get the type for",
                            update=SN_ScriptingBaseNode._evaluate)


    def evaluate(self, context):
        if self.node:
            self.outputs["Idname"].python_value = f"'{self.nodes[self.node].identifier}'"
        else:
            self.outputs["Idname"].python_value = "''"


    def draw_node(self, context, layout):
        layout.prop_search(self, "node", self, "nodes", text="")