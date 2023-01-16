import bpy
from ..base_node import SN_ScriptingBaseNode
from ..Input.Node_Idname import NodeType

class SN_NodeIsIdname(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_NodeIsIdname"
    bl_label = "Node Is Idname"
    node_color = "PROPERTY"


    nodes: bpy.props.CollectionProperty(type=NodeType)
        
    node: bpy.props.StringProperty(name="Node",
                            description="The node to get the type for",
                            update=SN_ScriptingBaseNode._evaluate)

    def on_create(self, context):
        self.add_property_input("Node")
        self.add_boolean_output("Is ID Name")
       
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


    def evaluate(self, context):
        if self.node:
            self.outputs[0].python_value = f"{self.inputs[0].python_value}.bl_rna.identifier == '{self.nodes[self.node].identifier}'"
        else:
            self.outputs[0].python_value = "False"


    def draw_node(self, context, layout):
        layout.prop_search(self, "node", self, "nodes", text="")

