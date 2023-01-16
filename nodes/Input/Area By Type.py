import bpy
from ..base_node import SN_ScriptingBaseNode



class SN_AreaByTypeNode(SN_ScriptingBaseNode, bpy.types.Node):

    bl_idname = "SN_AreaByTypeNode"
    bl_label = "Area By Type"
    node_color = "PROPERTY"
    
    def on_create(self, context):
        self.add_property_input("Screen")
        self.add_property_output("First Area")
        self.add_property_output("Last Area")
        self.add_property_output("Biggest Area")
        self.add_list_output("All Areas")
        self.add_boolean_output("Area Exists")
        self.add_integer_output("Area Amount")
        
        
    def area_items(self,context):
        types = ["VIEW_3D", "IMAGE_EDITOR", "NODE_EDITOR", "SEQUENCE_EDITOR",
                 "CLIP_EDITOR", "DOPESHEET_EDITOR", "GRAPH_EDITOR", "NLA_EDITOR",
                 "TEXT_EDITOR", "CONSOLE", "INFO", "TOPBAR", "STATUSBAR", "OUTLINER",
                 "PROPERTIES", "FILE_BROWSER", "PREFERENCES"]
        items = []
        for a_type in types:
            items.append((a_type,a_type.replace("_"," ").title(),a_type))
        return items
        
    area_type: bpy.props.EnumProperty(name="Area Type",
                                    description="The type of area to find",
                                    items=area_items,
                                    update=SN_ScriptingBaseNode._evaluate)

        
    def evaluate(self, context):
        self.code_imperative = f"""
            def find_areas_of_type(screen, area_type):
                areas = []
                for area in screen.areas:
                    if area.type == area_type:
                        areas.append(area)
                return areas

            def find_area_by_type(screen, area_type, index):
                areas = find_areas_of_type(screen, area_type)
                if areas:
                    return areas[index]
                return None

            def find_biggest_area_by_type(screen, area_type):
                areas = find_areas_of_type(screen, area_type)
                if not areas: return []
                max_area = (areas[0], areas[0].width * areas[0].height)
                for area in areas:
                    if area.width * area.height > max_area[1]:
                        max_area = (area, area.width * area.height)
                return max_area[0]
            """
        
        screen = "bpy.context.screen" if not "Screen" in self.inputs else self.inputs["Screen"].python_value
        self.outputs["First Area"].python_value = f"find_area_by_type({screen}, '{self.area_type}', 0)"
        self.outputs["Last Area"].python_value = f"find_area_by_type({screen}, '{self.area_type}', -1)"
        self.outputs["Biggest Area"].python_value = f"find_biggest_area_by_type({screen}, '{self.area_type}')"
        self.outputs["All Areas"].python_value = f"find_areas_of_type({screen}, '{self.area_type}')"
        self.outputs["Area Exists"].python_value = f"bool(find_areas_of_type({screen}, '{self.area_type}'))"
        self.outputs["Area Amount"].python_value = f"len(find_areas_of_type({screen}, '{self.area_type}'))"


    def draw_node(self, context, layout):
        layout.prop(self, "area_type", text="")