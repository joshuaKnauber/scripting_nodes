import operator
import bpy



class SN_OT_AddGenerateItemsNode(bpy.types.Operator):
    bl_idname = "sn.add_generate_items_node"
    bl_label = "Generate Items"
    bl_description = "Adds a node to generate dynamic enum items"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}

    def execute(self, context):
        bpy.ops.node.add_node("INVOKE_DEFAULT", type="SN_GenerateEnumItemsNode", use_transform=True)
        node = context.space_data.node_tree.nodes.active
        if context.scene.sn.property_index < len(context.scene.sn.properties):
            prop = context.scene.sn.properties[context.scene.sn.property_index]
            node.prop_name = prop.name
        return {"FINISHED"}
