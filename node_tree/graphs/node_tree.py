import bpy
from ..sockets.conversions import CONVERSIONS
from .node_refs import NodeRefCollection
from ...addon.variables.variables import SN_VariableProperties
from ...utils import unique_collection_name, get_python_name



class ScriptingNodesTree(bpy.types.NodeTree):

    bl_idname = 'ScriptingNodesTree'
    bl_label = "Visual Scripting Editor"
    bl_icon = 'FILE_SCRIPT'
    is_sn = True
    type: bpy.props.EnumProperty(items=[("SCRIPTING", "Scripting", "Scripting")], name="Type")

    index: bpy.props.IntProperty(default=0,
                            description="The index of this node tree in the node tree list",
                            name="Index")
    
    category: bpy.props.StringProperty(name="Category", default="OTHER",
                            description="The category this property is displayed in")

    link_cache = {} # stores cache of the links from the previous update for all node trees based on their memory adress


    variables: bpy.props.CollectionProperty(type=SN_VariableProperties,
                                        name="Variables",
                                        description="The variables of this node tree")

    variable_index: bpy.props.IntProperty(name="Variable Index", min=0,
                                        description="Index of the selected variable")
    

    node_refs: bpy.props.CollectionProperty(type=NodeRefCollection,
                                        name="Node References",
                                        description="A collection of groups that hold references to nodes of a specific idname")


    # cache python names so they only have to be generated once
    cached_python_names = {}
    cached_python_name: bpy.props.StringProperty()
    cached_human_name: bpy.props.StringProperty()
    
    @property
    def python_name(self):
        if self.name == self.cached_human_name and self.cached_python_name: return self.cached_python_name
        if self.name in self.cached_python_names: return self.cached_python_names[self.name]
        
        names = []
        for ntree in bpy.data.node_groups:
            if ntree.bl_idname == "ScriptingNodesTree":
                if ntree == self:
                    break
                names.append(ntree.python_name)
        
        name = unique_collection_name(f"{get_python_name(self.name, 'node_tree')}", "node_tree", names, "_")
        try:
            self.cached_python_name = name
            self.cached_human_name = self.name
        except AttributeError: pass
        self.cached_python_names[self.name] = name
        return name

    
    def node_collection(self, idname):
        """ Returns the collection for the given node idname refs in this node trees """
        if idname in self.node_refs:
            return self.node_refs[idname]
        return self.node_refs["empty"]
    

    def _map_link_to_sockets(self, link):
        """ Maps the given link to a tuple of the from socket, to socket and the link itself """
        from_real = None
        if getattr(link.to_socket, "is_sn", False):
            from_real = link.to_socket.from_socket()
        return (link.from_socket, link.to_socket, from_real, link)


    def is_valid_connection(self, from_out, to_inp):
        """ Check if a connection between the given sockets would be valid """
        if from_out and from_out.is_program == to_inp.is_program:
            # check if multiple program sockets are connected
            if to_inp.is_program:
                to_sockets = from_out.to_sockets(check_validity=False)
                if from_out.bl_label == to_inp.bl_label:
                    # check if first same program socket
                    for socket in to_sockets:
                        if socket.bl_label == to_inp.bl_label:
                            if socket == to_inp: return True
                            else: break
                return False
            # data types are the same
            elif from_out.bl_label == to_inp.bl_label:
                return True
            # check if data types are convertible
            else:
                if not to_inp.convert_data:
                    return True
                if from_out.bl_label in CONVERSIONS:
                    if to_inp.bl_label in CONVERSIONS[from_out.bl_label]:
                        return True
                return False
        return False

    def is_valid_link(self, link):
        """ Checks if the given link is valid """
        # all links connected to reroutes inputs are valid
        if not getattr(link.to_socket, "is_sn", False): return True

        # get the sockets and return their validity
        to_inp = link.to_socket
        from_out = link.to_socket.from_socket()
        return self.is_valid_connection(from_out, to_inp)
             
                
    def _insert_define_data_nodes(self, links):
        """ Inserts define data nodes for all links invalid links """
        for link in links:
            # add define data node
            if not getattr(link.from_socket, "changeable", False):
                node = self.nodes.new("SN_DefineDataType")
                if link.to_socket.bl_idname in list(map(lambda item: item[0], node.get_data_items(bpy.context))):
                    node.convert_to = link.to_socket.bl_idname
                node.location = ((link.from_node.location[0] + link.to_node.location[0]) / 2,
                                (link.from_node.location[1] + link.to_node.location[1]) / 2)
                self.links.new(link.from_socket, node.inputs[0])
                self.links.new(node.outputs[0], link.to_socket)
            # change data output
            elif link.from_socket.bl_label == "Data":
                to_sockets = link.from_socket.to_sockets(False)
                if not link.from_socket.dynamic and len(to_sockets) == 1:
                    to_socket = to_sockets[0]
                    if to_socket.bl_idname in list(map(lambda item: item[0], link.from_socket.get_data_type_items(bpy.context))):
                        link.from_socket.data_type = to_socket.bl_idname
                        link.from_socket.subtype = to_socket.subtype
                


    def _update_post(self):
        """ Only do visual aspects in here as this is run after evaluating the nodes """
        # mark links as invalid
        data_links = []
        for link in self.links:
            if not self.is_valid_link(link):
                link.is_valid = False
                if link.from_socket.bl_label == "Data":
                    data_links.append(link)
        self._insert_define_data_nodes(data_links)


    def _update_changed_links(self, links):
        """ Forces the affected nodes to update depending on if it's a program or data socket """
        for from_out, to_inp, _, _ in links:
            # update data sockets
            if getattr(to_inp, "is_sn", False) and not to_inp.is_program and to_inp.node:
                to_inp.force_update()
            # update program sockets
            elif getattr(from_out, "is_sn", False) and from_out.is_program and from_out.node:
                from_out.force_update()


    def _call_link_inserts(self, added):
        """ Calls link_insert for all new links """
        for from_inp, to_inp, from_real, _ in added:
            if from_real:
                from_real.node.link_insert(from_real, to_inp, is_output=True)
                to_inp.node.link_insert(from_real, to_inp, is_output=False)
            elif from_inp and getattr(from_inp.node, "is_sn", False) \
                and to_inp and getattr(to_inp.node, "is_sn", False):
                from_inp.node.link_insert(from_inp, to_inp, is_output=True)


    def _call_link_removes(self, removed):
        """ Calls link_remove for all removed links """
        for _, to_inp, from_real, _ in removed:
            if from_real:
                if from_real.node:
                    from_real.node.link_remove(from_real, to_inp, is_output=True)
                if to_inp.node:
                    to_inp.node.link_remove(from_real, to_inp, is_output=False)


    def _update_added_links(self, added):
        """ Triggers an update on the given links data outputs and program inputs to update the affected program """
        self._update_changed_links(added)
        self._call_link_inserts(added)

    def _update_removed_links(self, removed):
        """ Triggers an update on the given links data inputs and program outputs to update the affected program """
        self._update_changed_links(removed)
        self._call_link_removes(removed)


    def _update_tree_links(self):
        """ Finds all changed node links and updates the connections """
        # get current links
        curr_links = list(map(self._map_link_to_sockets, self.links.values()))

        if id(self) in self.link_cache:
            # update added links
            added = list(set(curr_links) - set(self.link_cache[id(self)]))
            self._update_added_links(added)
            # update removed links
            removed = list(set(self.link_cache[id(self)]) - set(curr_links))
            self._update_removed_links(removed)

        # update cached current links
        self.link_cache[id(self)] = curr_links

        # calls a function after the links are realized
        bpy.app.timers.register(self._update_post, first_interval=0.001)


    def _update_reroutes(self):
        """ Updates all inputs and display shapes of the reroutes in this node tree """
        for reroute in self.nodes:
            if reroute.bl_idname == "NodeReroute":
                try:
                    connections_left = [x.from_socket for x in reroute.inputs[0].links]
                    connections_right = [x.to_socket for x in reroute.outputs[0].links]
                    if reroute.inputs[0].bl_idname != "SN_RerouteSocket":
                        reroute.inputs.remove(reroute.inputs[0])
                        reroute.outputs.remove(reroute.outputs[0])
                        i = reroute.inputs.new("SN_RerouteSocket", "Input")
                        o = reroute.outputs.new("SN_RerouteSocket", "Output")
                        for c in connections_left:
                            self.links.new(c, i)
                        for c in connections_right:
                            self.links.new(c, o)
                    reroute.inputs[0].display_shape = connections_left[0].display_shape if connections_left else "CIRCLE"
                    reroute.outputs[0].display_shape = connections_left[0].display_shape if connections_left else "CIRCLE"
                except:
                    pass


    def update(self):
        # update tree links
        self._update_tree_links()
        self._update_reroutes()


    def reevaluate(self):
        """ Reevaluates all nodes in this node tree """
        # evaluate all nodes
        for node in self.nodes:
            if getattr(node, "is_sn", False):
                node._evaluate(bpy.context)