#SN_AddToPanelNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode
from ...operators.panel_ops import get_possible_panel_locations
from uuid import uuid4


class SN_AddToPanelNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_AddToPanelNode"
    bl_label = "Add To Panel"
    bl_icon = "MENU_PANEL"
    bl_width_default = 250
    node_color = (0.89,0.6,0)
    should_be_registered = True

    docs = {
        "text": ["This node adds <important>layouts to an existing panel.</>",
                "Press the 'Select Location' button to pick where your layouts should go."
                "",
                "Layout Output: You can add layouts to the panel here."],
        "python": ["<grey>def</> <function>add_this_to_panel</>(<blue>self</>, <blue>context</>):",
                   "    layout = self.layout",
                   "    layout.<function>label</>(text=<string>\"My label text\"</>, icon=<string>\"MONKEY\"</>)",
                   "",
                   "bpy.types.RENDER_PT_render.append(add_this_to_panel)"]
    }

    panel_idname: bpy.props.StringProperty()
    panel_name: bpy.props.StringProperty()
    append: bpy.props.BoolProperty()

    panel_uid: bpy.props.StringProperty()

    def inititialize(self,context):
        self.panel_uid = uuid4().hex[:10]
        self.sockets.create_output(self,"LAYOUT","Layout",True)

    def draw_buttons(self,context,layout):
        box = layout.box()
        row = box.row()
        row.scale_y = 1.5
        row.operator("visual_scripting.create_existing_panel_location",icon="EYEDROPPER",text="Select location").panel_uid = self.panel_uid

        row = layout.row()
        if not self.panel_idname:
            row.alert = True
            row.label(text="No location selected!")
        else:
            if not self.panel_name:
                row.label(text="'"+self.panel_idname+"' panel selected")
            else:
                row.label(text="'"+self.panel_name+"' panel selected")

    def layout_type(self):
        return "layout"

    def get_func_name(self):
        return "add_to_panel_"+self.panel_uid

    def get_register_block(self):
        if self.panel_idname:
            if self.append:
                return ["bpy.types."+self.panel_idname+".append("+self.get_func_name()+")"]
            return ["bpy.types."+self.panel_idname+".prepend("+self.get_func_name()+")"]
        return []

    def get_unregister_block(self):
        if self.panel_idname:
            return ["bpy.types."+self.panel_idname+".remove("+self.get_func_name()+")"]
        return []

    def evaluate(self, socket, node_data, errors):
        func_name = self.get_func_name()

        if self.panel_idname:
            panel_layout = []
            for output_data in node_data["output_data"]:
                if output_data["name"] == "Layout" and output_data["code"] != None:
                    panel_layout.append([output_data["code"]])
            
            return {
                "blocks": [
                    {
                        "lines": [
                            ["def ",func_name,"(self, context):"]
                        ],
                        "indented": [
                            ["layout = self.layout"],
                        ] + panel_layout
                    }
                ],
                "errors": errors
            }

        else:
            errors.append({
                "title": "No location selected",
                "message": "You need to select a location for the layout to live in",
                "node": self,
                "fatal": True
            })
            return {
                "blocks": [],
                "errors": errors
            }
