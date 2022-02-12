import bpy
from ..base_node import SN_ScriptingBaseNode



class NodeType(bpy.types.PropertyGroup):
    
    name: bpy.props.StringProperty()
    
    identifier: bpy.props.StringProperty()



class SN_NodeTypeNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_NodeTypeNode"
    bl_label = "Node Type"
    node_color = "STRING"

    def on_create(self, context):
        self.add_string_output("Type")
        
        # load python nodes
        for cls in bpy.types.NodeInternal.__subclasses__():
            item = self.nodes.add()
            item.name = cls.bl_rna.name
            item.name = f"{cls.bl_rna.name} (Internal)"
            item.identifier = cls.bl_rna.identifier
            for subcls in cls.__subclasses__():
                item = self.nodes.add()
                item.name = f"{subcls.bl_rna.name} ({cls.bl_rna.name})"
                item.identifier = subcls.bl_rna.identifier

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
            self.outputs["Type"].python_value = f"'{self.nodes[self.node].identifier}'"
        else:
            self.outputs["Type"].python_value = "''"


    def draw_node(self, context, layout):
        layout.prop_search(self, "node", self, "nodes", text="")