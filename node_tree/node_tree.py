import bpy


class ScriptingNodesTree(bpy.types.NodeTree):

    bl_idname = 'ScriptingNodesTree'
    bl_label = "Visual Scripting"
    bl_icon = 'FILE_SCRIPT'

    link_cache = {} # stores cache of the links from the previous update for all node trees based on their memory adress

    def update(self):
        curr_links = self.links.values()
        if not id(self) in self.link_cache:
            self.link_cache[id(self)] = curr_links
        else:
            diff = set(self.link_cache[id(self)]) ^ set(curr_links)
            print(diff)
            self.link_cache[id(self)] = curr_links
        print("update tree")