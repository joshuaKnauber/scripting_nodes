import bpy
import re
from ...node_tree.base_node import SN_ScriptingBaseNode


def sn_append_menu(self, context):
    row = self.layout.row()
    row.alert = True
    op = row.operator("sn.select_add_to_menu",text="Append Menu",icon="EYEDROPPER")
    op.menu = self.bl_idname
    op.append = True


def sn_prepend_menu(self, context):
    row = self.layout.row()
    row.alert = True
    op = row.operator("sn.select_add_to_menu",text="Prepend Menu",icon="EYEDROPPER")
    op.menu = self.bl_idname
    op.append = False


remove_menus = []
menu_node = None


class SN_OT_StartAddToMenuSelection(bpy.types.Operator):
    bl_idname = "sn.start_add_to_menu_selection"
    bl_label = "Select Menu"
    bl_description = "Start Menu Selection"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}
    
    node: bpy.props.StringProperty()
    
    @classmethod
    def poll(cls, context):
        global remove_menus
        return len(remove_menus) == 0
    
    def get_menus(self):
        menus = []
        for menu_name in dir(bpy.types):
            try:
                menu = eval("bpy.types."+menu_name)
                if hasattr(menu.bl_rna.base,"identifier") and menu.bl_rna.base.identifier == "Menu":
                    menus.append(menu_name)
            except:
                pass
        return menus

    def execute(self, context):
        global menu_node
        global remove_menus
        menu_node = context.space_data.node_tree.nodes[self.node]
        for menu in self.get_menus():
            try:
                eval("bpy.types."+menu+".append(sn_append_menu)")
                eval("bpy.types."+menu+".prepend(sn_prepend_menu)")
                remove_menus.append(eval("bpy.types."+menu))
            except:
                pass
        for area in context.screen.areas:
            area.tag_redraw()
        return {"FINISHED"}
    
    
def remove_registered_menus():
    global remove_menus
    for menu in remove_menus:
        try:
            menu.remove(sn_append_menu)
            menu.remove(sn_prepend_menu)
        except:
            pass
    remove_menus.clear()
    
    
class SN_OT_SelectAddToMenu(bpy.types.Operator):
    bl_idname = "sn.select_add_to_menu"
    bl_label = "Select Location"
    bl_description = "Select this location for your menu"
    bl_options = {"REGISTER", "INTERNAL", "UNDO"}
    
    menu: bpy.props.StringProperty(options={"SKIP_SAVE","HIDDEN"})
    append: bpy.props.BoolProperty(options={"SKIP_SAVE","HIDDEN"})

    def execute(self, context):
        global menu_node
        if menu_node:
            menu_node.menu = self.menu
            menu_node.position = "APPEND" if self.append else "PREPEND"
        menu_node = None
        remove_registered_menus()
        for area in context.screen.areas:
            area.tag_redraw()
        return {"FINISHED"}




class SN_AddToMenuNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_AddToMenuNode"
    bl_label = "Add To Menu"
    # bl_icon = "GRAPH"
    bl_width_default = 200
    
    node_options = {
        "default_color": (0.2,0.2,0.2),
        "starts_tree": True,
        "register_order": 1
    }
    
    
    menu: bpy.props.StringProperty(default="VIEW3D_MT_add")
    
    pie_menu: bpy.props.BoolProperty(default=False,name="Pie Menu",description="Add to pie menu")
    
    
    position: bpy.props.EnumProperty(items=[("PREPEND","Beginning","Prepend"), ("APPEND","End","Append")],
                                    name="Append/Prepend",
                                    description="Append or prepend the interface to the selected menu")
    

    def on_create(self,context):
        self.add_interface_output("Menu")
        self.add_dynamic_interface_output("Menu")


    def draw_node(self,context,layout):
        row = layout.row()
        row.scale_y = 1.5
        name = self.menu
        if "_" in name:
            name = name.replace("_MT_"," ").replace("_"," ").title()
        row.operator("sn.start_add_to_menu_selection",text=name,icon="EYEDROPPER").node = self.name
        layout.prop(self, "position", expand=True)
        layout.prop(self,"pie_menu")
        
        
    def what_layout(self, socket):
        return "layout"
    
    
    def function_name(self):
        return f"sn_{'append' if self.position == 'APPEND' else 'prepend'}_menu_{self.uid}"
    

    def code_evaluate(self, context, touched_socket):

        name = self.menu
        if "_" in name:
            name = name.replace("_PT_"," ").replace("_"," ").title()
        
        return {
            "code": f"""
                    def {self.function_name()}(self,context):
                        try:
                            layout = self.layout
                            {"layout = layout.menu_pie()" if self.pie_menu else ""}
                            {self.outputs[0].by_name(7)}
                        except Exception as exc:
                            print(str(exc) + " | Error in {name} when adding to menu")
                    """
        }
        
    
    def code_register(self, context):     
        return {
            "code": f"""
                    bpy.types.{self.menu}.{"append" if self.position == "APPEND" else "prepend"}({self.function_name()})
                    
                    """
        }
        
    
    def code_unregister(self, context):
        return {
            "code": f"""
                    bpy.types.{self.menu}.remove({self.function_name()})
                    
                    """
        }