import bpy
import re
import functools
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
        "has_collection": False,
        "collection_name_attr": "name",
        "starts_tree": False,
        "register_order": 0,
        "import_once": True,
        "evaluate_once": False,
        "register_once": False,
        "unregister_once": False,
        "imperative_once": False
    }
    
    node_tree_uid: bpy.props.StringProperty()
    addon_tree_uid: bpy.props.StringProperty()
    
    @property
    def node_tree(self):
        for tree in bpy.data.node_groups:
            if tree.sn_uid == self.node_tree_uid:
                return tree
    
    @property
    def addon_tree(self):
        for tree in bpy.data.node_groups:
            if tree.sn_uid == self.addon_tree_uid:
                return tree
    
    
    uid: bpy.props.StringProperty()


    @classmethod
    def poll(cls, ntree):
        return ntree.bl_idname == 'SN_ScriptingNodesTree'
    

    def on_any_change(self): pass


    def auto_compile(self,context=None):
        self.on_any_change()
        self.node_tree.set_changes(True)
        self.update_item_name()
        
        
    ### UPDATE FROM NODE PER TYPE
    def on_outside_update(self,node): pass
    
    def update_from_collection(self,collection,item): pass
    
    
    def update_nodes_by_type(self, idname):
        for graph in self.addon_tree.sn_graphs:
            for node in graph.node_tree.nodes:
                if node.bl_idname == idname:
                    node.on_outside_update(self)


    def update_nodes_by_types(self, *idname_list):
        for graph in self.addon_tree.sn_graphs:
            for node in graph.node_tree.nodes:
                if node.bl_idname in idname_list:
                    node.on_outside_update(self)


    ### REMOVE SOCKETS

    def remove_output_range(self, start_index, end_index=-1):
        """Both Parameters Inclusive"""
        if end_index == -1:
            end_index = len(self.outputs)-1

        for i in range(end_index, start_index-1, -1):
            self.outputs.remove(self.outputs[i])


    def remove_input_range(self, start_index, end_index=-1):
        """Both Parameters Inclusive"""
        if end_index == -1:
            end_index = len(self.inputs)-1

        for i in range(end_index, start_index-1, -1):
            self.inputs.remove(self.inputs[i])


    ### DYNAMIC SOCKET ADD
    def on_dynamic_add(self,socket,connected_socket): pass
    def on_dynamic_remove(self,is_output): pass
    
    
    ### VAR NAME UPDATE
    def on_var_name_update(self,socket): pass
        
        
    ### PROPERTY GROUP
    @property
    def collection(self):
        return self.addon_tree.sn_nodes[self.bl_idname]


    @property
    def item(self):
        for item in self.collection.items:
            if item.node_uid == self.uid:
                return item
    
    
    def __create_property_group(self):
        if "has_collection" in self.node_options and self.node_options["has_collection"]:
            if not self.bl_idname in self.addon_tree.sn_nodes:
                self.addon_tree.sn_nodes.add().name = self.bl_idname


    def __add_self_to_property_group(self):
        if "has_collection" in self.node_options and self.node_options["has_collection"]:
            item = self.addon_tree.sn_nodes[self.bl_idname].items.add()
            item.node_uid = self.uid
            self.update_item_name(item)


    def __remove_self_from_property_group(self):
        if "has_collection" in self.node_options and self.node_options["has_collection"]:
            for index, item in enumerate(self.addon_tree.sn_nodes[self.bl_idname].items):
                if item.node_uid == self.uid:
                    self.addon_tree.sn_nodes[self.bl_idname].items.remove(index)
                    break
                
                
    def update_item_name(self,item=None):
        if "has_collection" in self.node_options and self.node_options["has_collection"]:
            if not item:
                item = self.item
            if item:
                if "collection_name_attr" in self.node_options:
                    item.name = getattr(self,self.node_options["collection_name_attr"])
                else:
                    item.name = self.name
                
                
    def add_required_to_collection(self,idnames):
        for idname in idnames:
            if not idname in self.addon_tree.sn_nodes:
                item = self.addon_tree.sn_nodes.add()
                item.name = idname


    ### INIT NODE
    def on_create(self,context): pass


    def init(self,context):
        self.node_tree_uid = bpy.context.space_data.node_tree.sn_uid
        self.addon_tree_uid = bpy.context.scene.sn.addon_tree().sn_uid
        self.uid = uuid4().hex[:5].upper()
        if "default_color" in self.node_options:
            self.color = self.node_options["default_color"]
        else:
            self.color = (0.3,0.3,0.3)
        self.use_custom_color = True
        self.__create_property_group()
        self.__add_self_to_property_group()
        self.auto_compile()
        self.on_create(context)


    ### COPY NODE
    def on_copy(self,node): pass


    def copy(self,node):
        self.node_tree_uid = bpy.context.space_data.node_tree.sn_uid
        self.uid = uuid4().hex[:5].upper()
        self.__add_self_to_property_group()
        self.auto_compile()
        self.on_copy(node)


    ### FREE NODE
    def on_free(self): pass


    def free(self):
        self.auto_compile()
        self.__remove_self_from_property_group()
        self.on_free()


    ### NODE UPDATE
    def on_node_update(self): pass
    
    
    # def update_link_drop(self):
    #     op = bpy.context.active_operator
    #     if op and op.bl_idname == "NODE_OT_select":
    #         bpy.ops.sn.run_add_menu("INVOKE_DEFAULT",node=self.name)


    def update(self):
        self.auto_compile()
        self.on_node_update()


    ### LINK UPDATE
    def on_link_insert(self,link): pass
    
    
    def __matching_out_link(self,temp_link):
        for out in self.outputs:
            if out == temp_link.from_socket:
                for link in out.links:
                    if link.to_socket == temp_link.to_socket:
                        return link
                    
                    
    def __matching_inp_link(self,temp_link):
        for inp in self.inputs:
            if inp == temp_link.to_socket:
                for link in inp.links:
                    if link.from_socket == temp_link.from_socket:
                        return link
                    
    
    def __real_link(self, temp_link):
        link = self.__matching_out_link(temp_link)
        if not link:
            link = self.__matching_inp_link(temp_link)
        return link


    def after_link_insert(self,link):
        link = self.__real_link(link)
        if link:
            if link.to_socket.group == link.from_socket.group:
                if self == link.to_node:
                    link.to_socket.update_socket(self,link)
                else:
                    link.from_socket.update_socket(self,link)

                self.on_link_insert(link)

            else:
                try: self.node_tree.links.remove(link)
                except: pass
            self.auto_compile()


    def insert_link(self,link):
        bpy.app.timers.register(functools.partial(self.after_link_insert, link), first_interval=0.001)


    ### NAME HANDLING
    def get_python_name(self,name,empty_name=""):
        python_name = re.sub(r'\W+', '', name.replace(" ","_").lower())
        if not python_name:
            python_name = empty_name
        if python_name and python_name[0].isnumeric():
            python_name = "sn_" + python_name
        return python_name


    def __name_is_unique(self,collection,name):
        count = 0
        for item in collection:
            item_name = item if type(item) == str else item.name
            if item_name == name:
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
                item_name = item if type(item) == str else item.name
                if separator in item_name and item_name.split(separator)[-1].isnumeric():
                    base_name = (separator).join(item_name.split(separator)[:-1])
                    if base_name == name:
                        max_num = max(max_num, int(item_name.split(separator)[-1]))
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
    def add_interface_input(self,label): return self.add_input("SN_InterfaceSocket",label)
    def add_interface_output(self,label): return self.add_output("SN_InterfaceSocket",label)
    def add_dynamic_interface_input(self,label): return self.add_input("SN_DynamicInterfaceSocket",label)
    def add_dynamic_interface_output(self,label): return self.add_output("SN_DynamicInterfaceSocket",label)

    def add_execute_input(self,label): return self.add_input("SN_ExecuteSocket",label)
    def add_execute_output(self,label): return self.add_output("SN_ExecuteSocket",label)
    def add_dynamic_execute_input(self,label): return self.add_input("SN_DynamicExecuteSocket",label)
    def add_dynamic_execute_output(self,label): return self.add_output("SN_DynamicExecuteSocket",label)

    def add_string_input(self,label): return self.add_input("SN_StringSocket",label)
    def add_string_output(self,label): return self.add_output("SN_StringSocket",label)
    def add_dynamic_string_input(self,label): return self.add_input("SN_DynamicStringSocket",label)
    def add_dynamic_string_output(self,label): return self.add_output("SN_DynamicStringSocket",label)

    def add_boolean_input(self,label): return self.add_input("SN_BooleanSocket",label)
    def add_boolean_output(self,label): return self.add_output("SN_BooleanSocket",label)
    def add_dynamic_boolean_input(self,label): return self.add_input("SN_DynamicBooleanSocket",label)
    def add_dynamic_boolean_output(self,label): return self.add_output("SN_DynamicBooleanSocket",label)

    def add_float_input(self,label): return self.add_input("SN_FloatSocket",label)
    def add_float_output(self,label): return self.add_output("SN_FloatSocket",label)
    def add_dynamic_float_input(self,label): return self.add_input("SN_DynamicFloatSocket",label)
    def add_dynamic_float_output(self,label): return self.add_output("SN_DynamicFloatSocket",label)

    def add_integer_input(self,label): return self.add_input("SN_IntegerSocket",label)
    def add_integer_output(self,label): return self.add_output("SN_IntegerSocket",label)
    def add_dynamic_integer_input(self,label): return self.add_input("SN_DynamicIntegerSocket",label)
    def add_dynamic_integer_output(self,label): return self.add_output("SN_DynamicIntegerSocket",label)

    def add_data_input(self,label): return self.add_input("SN_DataSocket",label)
    def add_data_output(self,label): return self.add_output("SN_DataSocket",label)
    def add_dynamic_data_input(self,label): return self.add_input("SN_DynamicDataSocket",label)
    def add_dynamic_data_output(self,label): return self.add_output("SN_DynamicDataSocket",label)

    def add_list_input(self,label): return self.add_input("SN_ListSocket",label)
    def add_list_output(self,label): return self.add_output("SN_ListSocket",label)
    def add_dynamic_list_input(self,label): return self.add_input("SN_DynamicListSocket",label)
    def add_dynamic_list_output(self,label): return self.add_output("SN_DynamicListSocket",label)

    def add_dynamic_variable_input(self,label): return self.add_input("SN_DynamicVariableSocket",label)
    def add_dynamic_variable_output(self,label): return self.add_output("SN_DynamicVariableSocket",label)

    def add_icon_input(self,label): return self.add_input("SN_IconSocket",label)
    def add_icon_output(self,label): return self.add_output("SN_IconSocket",label)

    def add_blend_data_input(self,label): return self.add_input("SN_BlendDataSocket",label)
    def add_blend_data_output(self,label): return self.add_output("SN_BlendDataSocket",label)
    
    prop_types = {
        "STRING": "SN_StringSocket",
        "BOOLEAN": "SN_BooleanSocket",
        "FLOAT": "SN_FloatSocket",
        "INT": "SN_IntegerSocket",
        "INTEGER": "SN_IntegerSocket",
        "ENUM": "SN_StringSocket",
        "POINTER": "SN_BlendDataSocket",
        "COLLECTION": "SN_BlendDataSocket"
    }

        
    def enum_items_as_string(self,prop):
        items = "["
        for item in prop.enum_items:
            items += f"(\"{item.identifier}\",\"{item.name}\",\"{item.description}\"),"
        return items + "]"
            
            
    def subtype_from_prop_subtype(self,prop_type,prop_subtype,prop_size):
        if prop_type == "ENUM": return "ENUM"
        if prop_subtype == "COLOR":
            if prop_size == 3: return "COLOR"
            elif prop_size == 4: return "COLOR_ALPHA"
        elif prop_size != -1:
            if prop_size == 3: return "VECTOR3"
            elif prop_size == 4: return "VECTOR4"
        elif prop_subtype == "FACTOR": return "FACTOR"
        elif prop_subtype in ["FILE_PATH", "FILEPATH"]: return "FILE"
        elif prop_subtype in ["DIR_PATH", "DIRPATH"]: return "DIRECTORY"
        return "NONE"
    
    
    def add_input_from_data(self,prop_data):
        inp = self.add_input(self.prop_types[prop_data["type"]],prop_data["name"])
        inp.subtype = self.subtype_from_prop_subtype(prop_data["type"],prop_data["subtype"],prop_data["size"])
        inp.variable_name = prop_data["identifier"]
        if prop_data["type"] == "ENUM":
            inp.enum_values = prop_data["items"]
            inp.is_set = prop_data["is_set"]
        return inp
    
    
    def add_output_from_data(self,prop_data):
        out = self.add_output(self.prop_types[prop_data["type"]],prop_data["name"])
        out.subtype = self.subtype_from_prop_subtype(prop_data["type"],prop_data["subtype"],prop_data["size"])
        out.variable_name = prop_data["identifier"]
        if prop_data["type"] == "ENUM":
            out.enum_values = prop_data["items"]
        return out


    def get_default_from_operator(self,identifier,operator_line):
        if operator_line != None:
            props = operator_line.split("(")[-1].split(")")[0]+","
            if identifier+"=" in props:
                default = props.split(identifier+"=")[-1].split(",")[0]
                default = default.replace("\"","")
                return default
        return None
        
        
    def add_input_from_prop(self,prop,operator_line=None):
        if prop.type in self.prop_types:
            name = prop.name
            if not name:
                name = prop.identifier.replace("_", " ").title()

            for inp in self.inputs:
                if inp.default_text == name:
                    name = prop.identifier.replace("_", " ").title()


            inp = self.add_input(self.prop_types[prop.type], name)
            inp.variable_name = prop.identifier
            size = -1
            if hasattr(prop,"array_length"):
                size = prop.array_length
            if not prop.type in ["POINTER", "COLLECTION"]:
                inp.subtype = self.subtype_from_prop_subtype(prop.type,prop.subtype,size)
            else:
                inp.subtype = "COLLECTION" if prop.type == "COLLECTION" else "NONE"

            if prop.type == "ENUM":
                if len(prop.enum_items):
                    inp.enum_values = self.enum_items_as_string(prop)
                    inp.is_set = prop.is_enum_flag
                else:
                    inp.subtype = "NONE"

            if not prop.type in ["POINTER", "COLLECTION"]:
                default = self.get_default_from_operator(prop.identifier,operator_line)
                if default != None:
                    inp.set_default(default)
                else:
                    if not "VECTOR" in inp.subtype and not "COLOR" in inp.subtype:
                        inp.set_default(prop.default)
                    else:
                        inp.set_default(tuple([prop.default]*prop.array_length))
            return inp


    def add_output_from_prop(self,prop):
        if prop.type in self.prop_types:
            name = prop.name
            if not name:
                name = prop.identifier.replace("_", " ").title()
            
            for out in self.outputs:
                if out.default_text == name:
                    name = prop.identifier.replace("_", " ").title()

            out = self.add_output(self.prop_types[prop.type], name)
            out.variable_name = prop.identifier
            size = -1
            if hasattr(prop,"array_length"):
                size = prop.array_length
            if not prop.type in ["POINTER", "COLLECTION"]:
                out.subtype = self.subtype_from_prop_subtype(prop.type,prop.subtype,size)
            else:
                out.subtype = "COLLECTION" if prop.type == "COLLECTION" else "NONE"

            if prop.type == "ENUM":
                out.enum_values = self.enum_items_as_string(prop)
            return out
    
    
    def add_input(self,idname,label):
        self.auto_compile()
        socket = self.inputs.new(idname,label)
        socket.setup_socket(label)
        return socket
    
    
    def add_output(self,idname,label):
        self.auto_compile()
        socket = self.outputs.new(idname,label)
        socket.setup_socket(label)
        return socket
    
    
    def __change_socket(self, sockets, socket, idname):
        for i, sock in enumerate(sockets):
            if sock == socket:
                if socket.is_output:
                    new_socket = self.add_output(idname,socket.name)
                else:
                    new_socket = self.add_input(idname,socket.name)
                sockets.remove(socket)
                sockets.move(len(sockets)-1, i)
                return new_socket
    
    
    def change_socket_type(self,socket,idname):
        links = []
        for link in socket.links:
            links.append(link)
        if socket.is_output:
            new_socket = self.__change_socket(self.outputs,socket,idname)
            for link in links:
                if link.to_socket.group == new_socket.group:
                    self.node_tree.links.new(new_socket,link.to_socket)
        else:
            new_socket = self.__change_socket(self.inputs,socket,idname)
            for link in links:
                if new_socket.group == link.from_socket.group:
                    self.node_tree.links.new(link.from_socket,new_socket)
        return new_socket
            
    
    ### EVALUATE CODE
    
    
    def list_code(self, value_list, indents=0):
        return combine_blocks(value_list, indents)
        code = ""
        for i, value in enumerate(value_list):
            code += value
        return " "*indents*4 + code

    
    
    ### ERROR HANDLING
    
    
    def add_error(self, title, description, fatal=False):
        error = self.addon_tree.sn_graphs[0].errors.add()
        error.title = title
        error.description = description
        error.fatal = fatal
        error.node = self.name
        error.node_tree = self.addon_tree.sn_graphs[0].name


    ### RETURNED CODE
    def code_imports(self,context): pass
    def code_register(self,context): pass
    def code_unregister(self,context): pass
    def code_imperative(self,context): pass
    def code_evaluate(self,context,touched_socket): pass
    
    
    ### RETURNED TYPES
    def what_layout(self,socket): return "layout"
    
    def what_start_idname(self):
        for inp in self.inputs:
            if inp.group == "PROGRAM" and len(inp.links):
                return inp.links[0].from_node.what_start_idname()
        return self.bl_idname

    def what_start_node(self):
        for inp in self.inputs:
            if inp.group == "PROGRAM" and len(inp.links):
                return inp.links[0].from_node.what_start_node()
        return self



class SN_NodePropertyGroup(bpy.types.PropertyGroup):
    
    name: bpy.props.StringProperty()
    idname: bpy.props.StringProperty()



class SN_GenericPropertyGroup(bpy.types.PropertyGroup):
    
    name: bpy.props.StringProperty()
    identifier: bpy.props.StringProperty()
    description: bpy.props.StringProperty()
    node_uid: bpy.props.StringProperty()
    
    def node(self):
        for graph in bpy.context.scene.sn.addon_tree().sn_graphs:
            for node in graph.node_tree.nodes:
                if not node.bl_idname in ["NodeFrame","NodeReroute"]:
                    if node.uid == self.node_uid:
                        return node
    
    

class SN_NodeCollection(bpy.types.PropertyGroup):
    
    name: bpy.props.StringProperty()
    items: bpy.props.CollectionProperty(type=SN_GenericPropertyGroup)