#SN_InsertKeyframeNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode


class SN_InsertKeyframeNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_InsertKeyframeNode"
    bl_label = "Insert Keyframe"
    bl_icon = "CONSOLE"
    node_color = (0.2, 0.2, 0.2)
    should_be_registered = False 

    docs = {
        "text": ["This node is used to <important>insert a keyframe</>.",
                "",
                "Object: <subtext>The data block you want to insert a keyframe for.</>",
                "Data Path: <subtext>The data path to what you want to keyframe. Use right-click + Copy Data Path on the property</>",
                "Frame: <subtext>The frame you want to insert a keyframe on.</>",
                "Index Array: <subtext>Enable if you are keyframing a part of an array like location.</>",
                "Array Index: <subtext>If you are keyframing an array like location, you can specify the index here. -1 keyframes the entire array.</>"],
        "python": ["bpy.data.objects[0].<function>keyframe_insert</>( data_path=<string>\"location\"</>, frame=<number>1</> )"]
    }

    def update_is_array(self,context):
        if self.is_array:
            self.sockets.create_input(self,"INTEGER","Array Index").set_value(-1)
        else:
            self.sockets.remove_input(self,self.inputs[-1])

    is_array: bpy.props.BoolProperty(default=False,name="Index Array",description="Use an index for one value of the array that is being keyframed",update=update_is_array)

    def inititialize(self,context):
        self.sockets.create_input(self,"EXECUTE","Execute")
        self.sockets.create_input(self,"OBJECT","Input")
        self.sockets.create_input(self,"STRING","Data Path")
        self.sockets.create_input(self,"INTEGER","Frame")
        self.sockets.create_output(self,"EXECUTE","Execute")

    def draw_buttons(self,context,layout):
        layout.prop(self,"is_array")

    def evaluate(self, socket, node_data, errors):
        next_code = ""
        if node_data["output_data"][0]["code"]:
            next_code = node_data["output_data"][0]["code"]

        array_index = []
        if self.is_array:
            array_index = [", index=",node_data["input_data"][4]["code"]]
        
        return {
            "blocks": [
                {
                    "lines": [
                        ["if hasattr(", node_data["input_data"][1]["code"] ,",\"keyframe_insert\"):"]
                    ],
                    "indented": [
                        ["try: ", node_data["input_data"][1]["code"] ,".keyframe_insert(data_path=", node_data["input_data"][2]["code"] ,", frame=",node_data["input_data"][3]["code"]]+array_index+[")"],
                        ["except: self.report({\"WARNING\"},message=\"Couldn't insert this keyframe type on this input object\")"]
                    ]
                },
                {
                    "lines": [
                        ["else:"]
                    ],
                    "indented": [
                        ["self.report({\"WARNING\"},message=\"Couldn't insert keyframe for this object\")"]
                    ]
                },
                {"lines": [[next_code]],"indented": []}
            ],
            "errors": errors
        }

