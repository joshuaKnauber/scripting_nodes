import bpy


class ScriptingNodesTree(bpy.types.NodeTree):

    bl_idname = 'ScriptingNodesTree'
    bl_label = "Visual Scripting"
    bl_icon = 'FILE_SCRIPT'
    is_sn = True

    link_cache = {} # stores cache of the links from the previous update for all node trees based on their memory adress

    def _map_link_to_sockets(self, link):
        return (link.from_socket, link.to_socket, link)

    def is_valid_connection(self, from_out, to_inp):
        if from_out and from_out.is_program == to_inp.is_program:
            # TODO: check if origin is a program socket and multiple connected
            # TODO: check if data types are convertible
            return True
        return False

    def is_valid_link(self, link):
        if not getattr(link.to_socket, "is_sn", False): return True

        to_inp = link.to_socket
        from_out = link.to_socket.from_socket()
        return self.is_valid_connection(from_out, to_inp)

    def _update_post(self):
        """ Only do visual aspects in here as this is run after evaluating the nodes """
        # TODO check time of this function to see if it impacts performance
        for link in self.links:
            if not self.is_valid_link(link):
                link.is_valid = False

    def _update_changed_links(self, links):
        """ Forces the affected nodes to update depending on if it's a program or data socket """
        for from_out, to_inp, _ in links:
            if getattr(to_inp, "is_sn", False) and not to_inp.is_program:
                to_inp.force_update()
            elif getattr(from_out, "is_sn", False) and from_out.is_program:
                from_out.force_update()

    def _udpate_added_links(self, added):
        """ Triggers an update on the given links data outputs and program inputs to update the affected program """
        self._update_changed_links(added)

    def _udpate_removed_links(self, removed):
        """ Triggers an update on the given links data inputs and program outputs to update the affected program """
        self._update_changed_links(removed)

    def update(self):
        curr_links = list(map(self._map_link_to_sockets, self.links.values()))

        if id(self) in self.link_cache:
            added = list(set(curr_links) - set(self.link_cache[id(self)]))
            removed = list(set(self.link_cache[id(self)]) - set(curr_links))
            self._udpate_added_links(added)
            self._udpate_removed_links(removed)

        self.link_cache[id(self)] = curr_links

        bpy.app.timers.register(self._update_post, first_interval=0.001)