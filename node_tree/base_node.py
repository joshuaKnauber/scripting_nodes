import bpy
import re
from .sockets.base_sockets import add_to_remove_links
from ..compiler.compiler import combine_blocks
from uuid import uuid4



class SN_ScriptingBaseNode:

    bl_width_default = 160
    bl_width_min = 40
    bl_width_max = 5000

    bl_icon = "NONE"
    bl_label = "Node"
    
    node_options = {
        "default_color": (0.3,0.3,0.3),
        "has_property_group": False,
        "starts_tree": False,
        "import_once": False,
        "evaluate_once": False,
        "register_once": False,
        "unregister_once": False,
        "imperative_once": False
    }
    
    node_tree: bpy.props.PointerProperty(type=bpy.types.NodeTree)
    
    uid: bpy.props.StringProperty()


    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'SN_ScriptingNodesTree'
    
    def update_needs_compile(self,context):
        self.node_tree.set_changes(True)


    ### INIT NODE
    def on_create(self,context): pass


    def init(self,context):
        self.node_tree = self.id_data
        self.node_tree.set_changes(True)
        self.uid = uuid4().hex[:5].upper()
        if "default_color" in self.node_options:
            self.color = self.node_options["default_color"]
        else:
            self.color = (0.3,0.3,0.3)
        self.use_custom_color = True
        self.on_create(context)


    ### COPY NODE
    def on_copy(self,node): pass


    def copy(self,node):
        self.node_tree = self.id_data
        self.uid = uuid4().hex[:5].upper()
        self.node_tree.set_changes(True)
        self.on_copy(node)


    ### FREE NODE
    def on_free(self): pass


    def free(self):
        self.node_tree.set_changes(True)
        self.on_free()


    ### NODE UPDATE
    def on_node_update(self): pass


    def update(self):
        self.node_tree.set_changes(True)
        self.on_node_update()


    ### LINK UPDATE
    def on_link_insert(self,link): pass


    def insert_link(self,link):
        self.node_tree.set_changes(True)
        to_idname = link.to_socket.bl_idname
        from_idname = link.from_socket.bl_idname
        if from_idname in link.to_socket.connects_to and to_idname in link.from_socket.connects_to:
            if self == link.to_node:
                link.to_socket.update_socket(self,link)
            else:
                link.from_socket.update_socket(self,link)
            self.on_link_insert(link)
        else:
            add_to_remove_links(link)

    ### NAME HANDLING
    def get_python_name(self,name,empty_name=""):
        python_name = re.sub(r'\W+', '', name.replace(" ","_").lower())
        if not python_name:
            python_name = empty_name
        return python_name


    def __name_is_unique(self,collection,name):
        count = 0
        for item in collection:
            if item.name == name:
                count += 1
        return count <= 1


    def get_unique_name(self,name,collection,separator="_"):
        if self.__name_is_unique(collection, name):
            return name
        else:
            max_num = 0
            if separator in name and name.split(separator)[-1].isnumeric():
                name = (separator).join(name.split(separator)[:-1])
            for item in collection:
                if separator in item.name and item.name.split(separator)[-1].isnumeric():
                    item_name = (separator).join(item.name.split(separator)[:-1])
                    if item_name == name:
                        max_num = max(max_num, int(item.name.split(separator)[-1]))
            return name + separator + str(max_num+1).zfill(3)

    def get_unique_python_name(self,name,empty_name,collection,separator="_"):
        return self.get_unique_name(self.get_python_name(name, empty_name), collection, separator)



    ### DRAW NODE
    def draw_node(self,context,layout): pass


    def draw_buttons(self,context,layout):
        self.draw_node(context,layout)


    ### DRAW NODE PANEL
    def draw_node_panel(self,context,layout): pass


    def draw_buttons_ext(self,context,layout):
        self.draw_node_panel(context,layout)
        

    ### CREATE SOCKETS
    def add_string_input(self,label,removable=False): return self.add_input("SN_StringSocket",label,removable)
    def add_string_output(self,label,removable=False): return self.add_output("SN_StringSocket",label,removable)
    def add_boolean_input(self,label,removable=False): return self.add_input("SN_BooleanSocket",label,removable)
    def add_boolean_output(self,label,removable=False): return self.add_output("SN_BooleanSocket",label,removable)
    def add_float_input(self,label,removable=False): return self.add_input("SN_FloatSocket",label,removable)
    def add_float_output(self,label,removable=False): return self.add_output("SN_FloatSocket",label,removable)
    def add_icon_input(self,label,removable=False): return self.add_input("SN_IconSocket",label,removable)
    def add_icon_output(self,label,removable=False): return self.add_output("SN_IconSocket",label,removable)
    def add_data_input(self,label,removable=False): return self.add_input("SN_DataSocket",label,removable)
    def add_data_output(self,label,removable=False): return self.add_output("SN_DataSocket",label,removable)
    def add_dynamic_data_input(self,label): return self.add_input("SN_DynamicDataSocket",label,False)
    def add_dynamic_data_output(self,label): return self.add_output("SN_DynamicDataSocket",label,False)
    def add_execute_input(self,label,removable=False): return self.add_input("SN_ExecuteSocket",label,removable)
    def add_execute_output(self,label,removable=False): return self.add_output("SN_ExecuteSocket",label,removable)
    def add_dynamic_execute_input(self,label): return self.add_input("SN_DynamicExecuteSocket",label,False)
    def add_dynamic_execute_output(self,label): return self.add_output("SN_DynamicExecuteSocket",label,False)
    def add_interface_input(self,label,removable=False): return self.add_input("SN_InterfaceSocket",label,removable)
    def add_interface_output(self,label,removable=False): return self.add_output("SN_InterfaceSocket",label,removable)
    def add_dynamic_interface_input(self,label): return self.add_input("SN_DynamicInterfaceSocket",label,False)
    def add_dynamic_interface_output(self,label): return self.add_output("SN_DynamicInterfaceSocket",label,False)
    
    
    def add_input(self,idname,label,removable):
        self.node_tree.set_changes(True)
        socket = self.inputs.new(idname,label)
        socket.setup_socket(removable,label)
        return socket
    
    
    def add_output(self,idname,label,removable):
        self.node_tree.set_changes(True)
        socket = self.outputs.new(idname,label)
        socket.setup_socket(removable,label)
        return socket
    
    
    ### EVALUATE CODE
    
    
    def list_values(self, value_list, indents):
        code = ""
        for value in value_list:
            code += " "*indents*4 + value + "\n"
        if len(code) >= indents*4:
            return code[indents*4:]
        return code
    
    
    def list_blocks(self, block_list, indents):
        return combine_blocks(block_list, indents)
    
    
    ### ERROR HANDLING
    
    
    def add_error(self, title, description, fatal):
        error = bpy.context.scene.sn.addon_tree().sn_graphs[0].errors.add()
        error.title = title
        error.description = description
        error.fatal = fatal
        error.node = self.name
        error.node_tree = self.node_tree.sn_graphs[0].name


    ### RETURNED CODE
    def code_imports(self,context,main_tree): pass
    def code_register(self,context,main_tree): pass
    def code_unregister(self,context,main_tree): pass
    def code_imperative(self,context,main_tree): pass
    def code_evaluate(self,context,main_tree,touched_socket): pass
    
    
    ### RETURNED TYPES
    def what_layout(self,socket): return "layout"



class SN_GenericPropertyGroup(bpy.types.PropertyGroup):
    
    name: bpy.props.StringProperty(name="Name",
                                    description="The ")
    identifier: bpy.props.StringProperty()
    description: bpy.props.StringProperty()
    node_uid: bpy.props.StringProperty()