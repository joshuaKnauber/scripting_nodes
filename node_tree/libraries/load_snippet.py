import bpy
import os
import json


class SN_OT_LoadSnippet(bpy.types.Operator):
    bl_idname = "sn.load_snippet"
    bl_label = "Load Snippet"
    bl_description = "Loads the snippet"
    bl_options = {"REGISTER","UNDO","INTERNAL"}


    def deselect_nodes(self,ntree):
        for node in ntree.nodes:
            node.select = False


    def add_nodes(self,ntree,data):
        for node_data in data["nodes"]:
            node = ntree.nodes.new(node_data["bl_idname"])
            node_data["node"] = node
            for identifier in node_data["properties"]:
                if hasattr(node,identifier):
                    try: setattr(node,identifier,node_data["properties"][identifier])
                    except: pass


    def get_node_by_name(self,data,name):
        for node_data in data["nodes"]:
            if node_data["properties"]["name"] == name:
                return node_data["node"]


    def add_links(self,ntree,data):
        for node_data in data["nodes"]:
            for index, inp_data in enumerate(node_data["inputs"]):
                for link_data in inp_data:
                    try: ntree.links.new(node_data["node"].inputs[index], self.get_node_by_name(data,link_data["name"]).outputs[link_data["index"]])
                    except: pass

            for index, out_data in enumerate(node_data["outputs"]):
                for link_data in out_data:
                    try: ntree.links.new(node_data["node"].outputs[index], self.get_node_by_name(data,link_data["name"]).inputs[link_data["index"]])
                    except: pass


    def execute(self, context):
        ntree = context.space_data.node_tree

        with open(os.path.join(os.path.dirname(__file__),"snippet.json"),"r+") as f:
            data = json.loads(f.read())
            self.deselect_nodes(ntree)
            self.add_nodes(ntree,data)
            self.add_links(ntree,data)
        return {"FINISHED"}
