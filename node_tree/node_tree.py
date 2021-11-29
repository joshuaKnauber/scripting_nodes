import bpy


class ScriptingNodesTree(bpy.types.NodeTree):

    bl_idname = 'ScriptingNodesTree'
    bl_label = "Visual Scripting"
    bl_icon = 'FILE_SCRIPT'

    link_cache = {} # stores cache of the links from the previous update for all node trees based on their memory adress

    def _map_link_to_sockets(self, link):
        return (link.from_socket, link.to_socket)

    def update(self):
        curr_links = map(self._map_link_to_sockets, self.links.values())
        if not id(self) in self.link_cache:
            self.link_cache[id(self)] = curr_links
        # else:
        #     diff = set(self.link_cache[id(self)]) ^ set(curr_links)
        #     self.link_cache[id(self)] = curr_links
        print([(a.node.name, b.node.name) for a,b in self.link_cache[id(self)]])
        print("update tree")