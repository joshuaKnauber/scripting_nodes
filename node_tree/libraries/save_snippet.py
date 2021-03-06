import bpy
import os
import json



class SN_OT_SaveSnippet(bpy.types.Operator):
    bl_idname = "sn.save_snippet"
    bl_label = "Save Snippet"
    bl_description = "Save Snippet"
    bl_options = {"REGISTER","UNDO","INTERNAL"}


    def selected(self,context):
        selected = []
        for node in context.space_data.node_tree.nodes:
            if node.select:
                selected.append(node)
        return selected


    def get_node_specific_properties(self,node):
        properties = {}
        for prop in node.bl_rna.properties:
            if not prop.identifier in bpy.types.Node.bl_rna.properties and not prop.type in ["POINTER","COLLECTION"]:
                if not hasattr(prop,"is_array") or (hasattr(prop,"is_array") and not prop.is_array):
                    properties[prop.identifier] = getattr(node,prop.identifier)
                else:
                    properties[prop.identifier] = tuple(getattr(node,prop.identifier))
        return properties


    def get_from_index(self,node,socket):
        for index, out in enumerate(node.outputs):
            if out == socket:
                return index


    def get_to_index(self,node,socket):
        for index, inp in enumerate(node.inputs):
            if inp == socket:
                return index


    def get_node_inputs(self,node):
        inputs = []
        # save socket value if exists
        for inp in node.inputs:
            links = []
            for link in inp.links:
                if link.from_node.select:
                    links.append( {"name":link.from_node.name, "index":self.get_from_index(link.from_node,link.from_socket)} )
            inputs.append(links)
        return inputs


    def get_node_outputs(self,node):
        outputs = []
        for out in node.outputs:
            links = []
            for link in out.links:
                if link.to_node.select:
                    links.append( {"name":link.to_node.name, "index":self.get_to_index(link.to_node,link.to_socket)} )
            outputs.append(links)
        return outputs


    def get_node_data(self,node):
        data = {
            "bl_idname": node.bl_idname,
            "properties": {
                "name": node.name,
                "label": node.label,
                "use_custom_color": node.use_custom_color,
                "color": tuple(node.color),
                "location": (node.location[0], node.location[1])
            },
            "inputs": [],
            "outputs": []
        }

        data["properties"] = {**data["properties"], **self.get_node_specific_properties(node)}
        del data["properties"]["uid"]

        data["inputs"], data["outputs"] = self.get_node_inputs(node), self.get_node_outputs(node)
        return data


    def get_selected_data(self,selected):
        data = {"nodes":[]}
        for node in selected:
            data["nodes"].append(self.get_node_data(node))
        return data


    def execute(self, context):
        data = json.dumps(self.get_selected_data(self.selected(context)), indent=4)
        with open(os.path.join(os.path.dirname(__file__),"snippet.json"),"r+") as f:
            f.write(data)
        return {"FINISHED"}

