import bpy
from uuid import uuid4


possible_locations = []
def get_possible_panel_locations():
    global possible_locations
    
    if not possible_locations:
        for panel in dir(bpy.types):
            panel = eval("bpy.types." + panel)
            if hasattr(panel,"bl_space_type") and hasattr(panel,"bl_region_type"):
                
                location = {"space":panel.bl_space_type, "region":panel.bl_region_type, "category":"", "context":""}
                if hasattr(panel,"bl_category"):
                    location["category"] = panel.bl_category
                if hasattr(panel,"bl_context"):
                    location["context"] = panel.bl_context

                if not location in possible_locations:
                    possible_locations.append(location)
                        
    return possible_locations[:]


trigger_node = None
def set_trigger_node(node):
    global trigger_node
    trigger_node = node

class SN_CreatePanelLocations(bpy.types.Operator):
    bl_idname = "visual_scripting.create_panel_locations"
    bl_label = "Create Panel Locations"
    bl_description = "Creates panels in all possible locations for you to pick one"
    bl_options = {"REGISTER","UNDO","INTERNAL"}

    trigger_node: bpy.props.StringProperty()

    @classmethod
    def poll(cls, context):
        for panel in dir(bpy.types):
            if "SN_PT_LocationPickerPanel_" in panel:
                return False
        return True

    def create_panels(self,locations):
        for location in locations:
            uid = uuid4().hex[:10]
            context = "bl_context='"+location["context"]+"'" if location["context"] else ""
            category = "bl_category='"+location["category"]+"'" if location["category"] else ""
            panel = f"""
class SN_PT_LocationPickerPanel_{uid}(bpy.types.Panel):
    bl_label = " "
    bl_idname = "SN_PT_LocationPickerPanel_{uid}"
    bl_space_type = '{location["space"]}'
    bl_region_type = '{location["region"]}'
    {context}
    {category}
    bl_options = {{"HIDE_HEADER"}}

    def draw(self, context):
        row = self.layout.row()
        row.alert = True
        row.scale_y = 2
        op = row.operator("visual_scripting.choose_panel_location",icon="EYEDROPPER")
        op.space = "{location["space"]}"
        op.region = "{location["region"]}"
        op.context = "{location["context"]}"
        op.category = "{location["category"]}"
        col = row.column()
        col.alert = False
        col.operator("visual_scripting.cancel_panel_location",icon="PANEL_CLOSE",text="",emboss=False)

bpy.utils.register_class(SN_PT_LocationPickerPanel_{uid})"""
            exec(panel)

    def execute(self, context):
        possible_locations = get_possible_panel_locations()
        self.create_panels(possible_locations)

        if self.trigger_node in context.space_data.node_tree.nodes:
            set_trigger_node(context.space_data.node_tree.nodes[self.trigger_node])
        return {"FINISHED"}



def remove_created_panels():
    global created_panels
    for panel in dir(bpy.types):
        if len(panel.split("_")) == 4 and panel.split("_")[2] == "LocationPickerPanel":
            bpy.utils.unregister_class(eval("bpy.types."+panel))



class SN_ChoosePanelLocation(bpy.types.Operator):
    bl_idname = "visual_scripting.choose_panel_location"
    bl_label = "Choose This Location"
    bl_description = "Choose this as the location of your panel"
    bl_options = {"REGISTER","UNDO","INTERNAL"}

    space: bpy.props.StringProperty()
    region: bpy.props.StringProperty()
    category: bpy.props.StringProperty()
    context: bpy.props.StringProperty()

    def execute(self, context):
        global trigger_node
        if trigger_node:
            trigger_node.space = self.space
            trigger_node.region = self.region
            if self.context:
                trigger_node.context = self.context
            else:
                trigger_node.context = "NONE"
            trigger_node = None
        remove_created_panels()
        return {"FINISHED"}



class SN_CancelPanelLocation(bpy.types.Operator):
    bl_idname = "visual_scripting.cancel_panel_location"
    bl_label = "Cancel Picking Panel Location"
    bl_description = "Cancel the picking of a panel location"
    bl_options = {"REGISTER","UNDO","INTERNAL"}

    def execute(self, context):
        remove_created_panels()
        return {"FINISHED"}



def prepend_panel(self, context, prepend=False):
    row = self.layout.row()
    row.scale_y = 1.2
    row.alert = True
    op = row.operator("visual_scripting.choose_existing_panel_location",icon="EYEDROPPER")
    op.prepend = prepend
    col = row.column()
    col.alert = False
    col.operator("visual_scripting.cancel_existing_panel_location",text="",emboss=False,icon="PANEL_CLOSE")

def append_panel(self, context):
    prepend_panel(self,context,True)

class SN_CreateExistingPanelLocation(bpy.types.Operator):
    bl_idname = "visual_scripting.create_existing_panel_location"
    bl_label = "Create Existing Panel"
    bl_description = "Create the possible panel locations"
    bl_options = {"REGISTER","UNDO","INTERNAL"}

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        for panel in dir(bpy.types):
            panel = eval("bpy.types."+panel)
            if hasattr(panel,"bl_space_type") and hasattr(panel,"bl_region_type"):
                panel.prepend(prepend_panel)
                panel.append(append_panel)
        return {"FINISHED"}


def remove_appended_panels():
    for panel in dir(bpy.types):
        panel = eval("bpy.types."+panel)
        if hasattr(panel,"bl_space_type") and hasattr(panel,"bl_region_type"):
            panel.remove(prepend_panel)
            panel.remove(append_panel)


class SN_ChooseExistingPanelLocation(bpy.types.Operator):
    bl_idname = "visual_scripting.choose_existing_panel_location"
    bl_label = "Choose This Location"
    bl_description = "Choose this panel as the location of your layout"
    bl_options = {"REGISTER","UNDO","INTERNAL"}

    panel_name: bpy.props.StringProperty()
    prepend: bpy.props.BoolProperty()

    def execute(self, context):
        for panel in dir(bpy.types):
            if panel == self.panel_name:
                panel = eval("bpy.types."+panel)
                print(panel,self.prepend)
        remove_appended_panels()
        return {"FINISHED"}


class SN_CancelExistingPanelLocation(bpy.types.Operator):
    bl_idname = "visual_scripting.cancel_existing_panel_location"
    bl_label = "Cancel Picking Panel"
    bl_description = "Cancel the picking of a panel"
    bl_options = {"REGISTER","UNDO","INTERNAL"}

    def execute(self, context):
        remove_appended_panels()
        return {"FINISHED"}