#SN_PanelNode

import bpy
from ...node_tree.base_node import SN_ScriptingBaseNode
from ...operators.panel_ops import get_possible_panel_locations
from uuid import uuid4


class SN_PanelNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_PanelNode"
    bl_label = "Panel"
    bl_icon = "MENU_PANEL"
    bl_width_default = 250
    node_color = (0.89,0.6,0)
    should_be_registered = True

    docs = {
        "text": ["This node adds a <important>panel to the interface.</>",
                "Press the 'Select Location' button to pick where the panel should be displayed"
                "",
                "Label: <subtext>This is the label that will be shown in the panels header.</>",
                "Hide Header: <subtext>This determines if the header of the panel should be shown or hidden.</>",
                "Default Closed: <subtext>If this is True, the panel will be closed by default.</>",
                "Show Panel: <subtext>This determines if the panel should be shown or hidden.</>"],
        "python": ["<function>class</> My_PT_Panel(bpy.types.Panel):",
                   "    bl_idname = <string>'My_PT_Panel'</>",
                   "    bl_label = <string>'My Panel'</>",
                   "    bl_space_type = <string>'PROPERTIES'</>",
                   "    bl_region_type = <string>'WINDOW'</>",
                   "    bl_context = <string>'object'</>",
                   "    bl_options = {<string>\"HIDE_HEADER\"</>}",
                   "",
                   "    <yellow>@classmethod</>",
                   "    <grey>def</> <function>poll</>(<blue>cls</>, <blue>context</>):",
                   "        return <red>True</>",
                   "",
                   "    <grey>def</> <function>draw</>(<blue>self</>, <blue>context</>):",
                   "        layout = self.layout",
                   "        layout.<function>label</>(text=<string>\"My label text\"</>, icon=<string>\"MONKEY\"</>)"]
    }

    def space_items(self,context):
        items = []
        for location in get_possible_panel_locations():
            has_value = False
            for item in items:
                if location["space"] == item[0]:
                    has_value = True
                    break
            if not has_value:
                items.append( (location["space"],location["space"].replace("_"," ").title(),location["space"]) )
        return items

    def region_items(self,context):
        items = []
        space = self.space
        for location in get_possible_panel_locations():
            if location["space"] == space:
                has_value = False
                for item in items:
                    if location["region"] == item[0]:
                        has_value = True
                        break
                if not has_value:
                    items.append( (location["region"],location["region"].replace("_"," ").title(),location["region"]) )
        return items

    def context_items(self,context):
        items = [("NONE","All Contexts","The panel will be shown in all contexts")]
        region = self.region
        space = self.space
        for location in get_possible_panel_locations():
            if location["space"] == space and location["region"] == region and location["context"]:
                has_value = False
                for item in items:
                    if location["context"] == item[0]:
                        has_value = True
                        break
                if not has_value:
                    items.append( (location["context"],location["context"].replace("_"," ").title(),location["context"]) )
        return items

    def category_items(self,context):
        items = [("CUSTOM","Custom Category","You can define a custom category the panel will be shown in")]
        region = self.region
        space = self.space
        for location in get_possible_panel_locations():
            if location["space"] == space and location["region"] == region and location["category"]:
                has_value = False
                for item in items:
                    if location["category"] == item[0]:
                        has_value = True
                        break
                if not has_value:
                    items.append( (location["category"],location["category"],location["category"]) )
        return items

    space: bpy.props.EnumProperty(name="Space",description="Space the panel should go in",items=space_items)
    region: bpy.props.EnumProperty(name="Region",description="Region the panel should go in",items=region_items)
    context: bpy.props.EnumProperty(name="Context",description="Context the panel should be shown in",items=context_items)
    category: bpy.props.EnumProperty(name="Category",description="Category the panel should be shown in",items=category_items)
    custom_category: bpy.props.StringProperty(name="Custom Category",description="Category the panel should be shown in",default="My Category")

    label: bpy.props.StringProperty(default="My Panel",name="Label", description="Name shown in the header of the panel")
    hide_header: bpy.props.BoolProperty(default=False,name="Hide Header", description="Hide the header of the panel")
    default_closed: bpy.props.BoolProperty(default=False,name="Default Closed", description="Close the panel by default")

    panel_uid: bpy.props.StringProperty()

    def inititialize(self,context):
        self.panel_uid = uuid4().hex[:10]
        self.sockets.create_input(self,"BOOLEAN","Show Panel")
        self.sockets.create_output(self,"LAYOUT","Header",True)
        self.sockets.create_output(self,"LAYOUT","Panel",True)

    def draw_buttons(self,context,layout):
        box = layout.box()
        row = box.row()
        row.scale_y = 1.5
        row.operator("visual_scripting.create_panel_locations",icon="EYEDROPPER",text="Select location").trigger_node = self.name

        msg = self.space.replace("_"," ").title()+" -> "+self.region.replace("_"," ").title()

        if len(self.context_items(context)) > 1:
            if self.context != "NONE":
                msg += " -> "+self.context.replace("_"," ").title()

        box.label(text=msg)
        if len(self.category_items(context)) > 1:
            col = box.column(align=True)
            col.prop(self,"category")
            if self.category == "CUSTOM":
                col.prop(self,"custom_category",text="Custom")
                
        layout.prop(self,"label")
        layout.prop(self,"hide_header")
        layout.prop(self,"default_closed")

    def layout_type(self):
        return "layout"

    def get_idname(self):
        return "SNA_PT_"+self.panel_uid

    def get_register_block(self):
        return ["bpy.utils.register_class("+self.get_idname()+")"]

    def get_unregister_block(self):
        return ["bpy.utils.unregister_class("+self.get_idname()+")"]

    def evaluate(self, socket, node_data, errors):
        idname = self.get_idname()

        label = self.label
        if label == "":
            label = " "

        context = []
        if len(self.context_items(context)) > 1:
            if not self.context == "NONE":
                context = ["bl_context = \"",self.context,"\""]

        category = []
        if len(self.context_items(context)) > 1:
            category = ["bl_category = \"",self.category,"\""]
            if self.category == "CUSTOM":
                if self.custom_category:
                    category = ["bl_category = \"",self.custom_category,"\""]
                else:
                    errors.append({
                        "title": "No category",
                        "message": "Please enter a category name",
                        "node": self,
                        "fatal": True
                    })
        
        options = ""
        if self.default_closed:
            options += "\"DEFAULT_CLOSED\""
        if self.hide_header:
            if options:
                options += ","
            options += "\"HIDE_HEADER\""
        if options:
            options = ["bl_options = {",options,"}"]
        else:
            options = []

        header_layout = []
        for output_data in node_data["output_data"]:
            if output_data["name"] == "Header" and output_data["code"] != None:
                header_layout.append([output_data["code"]])

        panel_layout = []
        for output_data in node_data["output_data"]:
            if output_data["name"] == "Panel" and output_data["code"] != None:
                panel_layout.append([output_data["code"]])
        
        return {
            "blocks": [
                {
                    "lines": [
                        ["class ",idname,"(bpy.types.Panel):"]
                    ],
                    "indented": [
                        ["bl_label = \"",label,"\""],
                        ["bl_idname = \"",idname,"\""],
                        ["bl_space_type = \"",self.space,"\""],
                        ["bl_region_type = \"",self.region,"\""],
                        context,
                        category,
                        options,

                        [""],
                        ["@classmethod"],
                        ["def poll(cls, context):"],
                        {
                            "lines": [],
                            "indented": [
                                ["return ",node_data["input_data"][0]["code"]],
                            ]
                        },
                        
                        [""],
                        ["def draw_header(self, context):"],
                        {
                            "lines": [],
                            "indented": [
                                ["layout = self.layout"],
                            ] + header_layout
                        },
                        
                        [""],
                        ["def draw(self, context):"],
                        {
                            "lines": [],
                            "indented": [
                                ["layout = self.layout"],
                            ] + panel_layout
                        },
                        [""],
                        [""],
                    ]
                }
            ],
            "errors": errors
        }
