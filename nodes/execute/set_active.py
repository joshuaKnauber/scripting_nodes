#SN_SetActiveNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_SetActiveNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_SetActiveNode"
    bl_label = "Set Active"
    bl_icon = "LAYER_ACTIVE"
    node_color = (0.2, 0.2, 0.2)
    should_be_registered = False

    docs = {
        "text": ["The Set Active Node is used to <important>set an active object, action or node</>.",
                "",
                "Object Input: <subtext>The object you want to set as active object</>",
                "Action Input: <subtext>The action you want to set as active action</>",
                "Nodes Input: <subtext>The nodes where you want to set your active node</>",
                "Node Input: <subtext>The node you want to set as active node</>"],
        "python": ["bpy.context.view_layer.objects.active = bpy.data.objects[0]"]

    }

    def update_type(self, context):
        if len(self.inputs) == 3:
            self.inputs.remove(self.inputs[2])

        if self.active_type == "object":
            self.sockets.change_socket_type(self, self.inputs[1], "OBJECT", "Object")
        elif self.active_type == "action":
            self.sockets.change_socket_type(self, self.inputs[1], "OBJECT", "Object")
            self.sockets.create_input(self, "OBJECT", "Action")
        else:
            self.sockets.change_socket_type(self, self.inputs[1], "OBJECT", "Node")
            self.sockets.create_input(self, "COLLECTION", "Nodes")

    active_type: bpy.props.EnumProperty(name="Type", items=[("object", "Object", ""), ("action", "Action", ""), ("node", "Node", "")], update=update_type)

    def reset_data_type(self, context):
        self.update_node()

    def inititialize(self,context):
        self.sockets.create_input(self,"EXECUTE","Execute")
        self.sockets.create_input(self,"OBJECT","Object")
        self.sockets.create_output(self,"EXECUTE","Execute")

    def update_node(self):
        if len(self.inputs) == 2:
            if len(self.inputs[1].links):
                if self.active_type == "object":
                    if self.inputs[1].links[0].from_node.data_type(self.inputs[1].links[0].from_socket) != "bpy.types.Object":
                        link = self.inputs[1].links[0]
                        bpy.context.space_data.node_tree.links.remove(link)

        elif len(self.inputs) == 3:
            if len(self.inputs[1].links):
                if self.active_type == "action":
                    if self.inputs[1].links[0].from_node.data_type(self.inputs[1].links[0].from_socket) != "bpy.types.Object":
                        link = self.inputs[1].links[0]
                        bpy.context.space_data.node_tree.links.remove(link)
                elif self.active_type == "node":
                    if "Node" in self.inputs[2].links[0].from_node.data_type(self.inputs[2].links[0].from_socket):
                        link = self.inputs[1].links[0]
                        bpy.context.space_data.node_tree.links.remove(link)

            if len(self.inputs[2].links):
                if self.active_type == "action":
                    if self.inputs[2].links[0].from_node.data_type(self.inputs[2].links[0].from_socket) != "bpy.types.Action":
                        link = self.inputs[2].links[0]
                        bpy.context.space_data.node_tree.links.remove(link)
                if self.active_type == "node":
                    if "Node" in self.inputs[2].links[0].from_node.data_type(self.inputs[2].links[0].from_socket):
                        link = self.inputs[2].links[0]
                        bpy.context.space_data.node_tree.links.remove(link)


    def draw_buttons(self, context, layout):
        layout.prop(self, "active_type", expand=True)

    def evaluate(self, socket, node_data, errors):
        next_code = ""
        if node_data["output_data"][0]["code"]:
            next_code = node_data["output_data"][0]["code"]

        if self.active_type == "object":
            active_object = "None"
            if node_data["input_data"][1]["code"]:
                active_object = node_data["input_data"][1]["code"]

            return {"blocks": [{"lines": [["bpy.context.view_layer.objects.active = ", active_object]],"indented": []},{"lines": [[next_code]],"indented": []}],"errors": errors}

        elif self.active_type == "node":
            active_node = "None"
            if node_data["input_data"][1]["code"]:
                active_node = node_data["input_data"][1]["code"]

            if node_data["input_data"][2]["code"]:
                nodes = node_data["input_data"][2]["code"]
            else:
                errors.append({"title": "No nodes provided", "message": "You need to put in the collecion of nodes where your node is", "node": self, "fatal": True})
                return {"blocks": [{"lines": [[next_code]],"indented": []}],"errors": errors}

            return {"blocks": [{"lines": [[nodes, ".active = ", active_node]],"indented": []},{"lines": [[next_code]],"indented": []}],"errors": errors}

        else:
            if node_data["input_data"][1]["code"]:
                object_input = node_data["input_data"][1]["code"]
            else:
                errors.append({"title": "No object provided", "message": "You need to put in the object you want to set the active action on", "node": self, "fatal": True})
                return {"blocks": [{"lines": [[next_code]],"indented": []}],"errors": errors}
            if node_data["input_data"][2]["code"]:
                active_action = node_data["input_data"][2]["code"]
            else:
                errors.append({"title": "No action provided", "message": "You need to put in the action you want to set as active action", "node": self, "fatal": True})
                return {"blocks": [{"lines": [[next_code]],"indented": []}],"errors": errors}

            return {"blocks": [{"lines": [[object_input, ".animation_data.action = ", active_action]],"indented": []},{"lines": [[next_code]],"indented": []}],"errors": errors}

