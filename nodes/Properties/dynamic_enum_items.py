# import bpy
# import json
# from ...node_tree.base_node import SN_ScriptingBaseNode
# from .property_util import get_data, setup_data_input, setup_data_output



# class SN_DynamicEnumItemsNode(bpy.types.Node, SN_ScriptingBaseNode):

#     bl_idname = "SN_DynamicEnumItemsNode"
#     bl_label = "On Dynamic Enum Items Update"
#     # bl_icon = "GRAPH"
#     bl_width_default = 200

#     node_options = {
#         "default_color": (0.3,0.3,0.3),
#     }

#     def on_create(self,context):
#         self.add_execute_output("Update Items")
#         self.add_list_output("Current Items")
#         # self.copied_path = self.copied_path

#     def on_copy(self, node):
#         # self.copied_path = ""
#         pass

#     def draw_node(self, context, layout):
#         if False:
#             row = layout.row()
#             row.alert = True
#             row.label(text="You need to add this node using a getter")


#     def code_imperative(self, context):

#         if False: #not self.copied_path:
#             self.add_error("No property", "You need to add this node from a property")
#             return {"code": ""}
        
#         identifier = "test"

#         return {
#             "code": f"""
#                     {identifier}_enum_items = []
#                     def items_{identifier}(self, context):
#                         global {identifier}_enum_items
#                         {self.outputs[0].code(6)}
#                         return {identifier}_enum_items if {identifier}_enum_items else [("NONE","NONE","This dynamic enum has no items")]
#                     """
#         }


#     def code_evaluate(self, context, touched_socket):
        
#         identifier = "test"

#         if touched_socket == self.outputs[1]:
#             return {
#                 "code": f"{identifier}_enum_items"
#             }

#         return {"code": ""}