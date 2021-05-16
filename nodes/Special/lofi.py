import bpy
from random import randint
from ...node_tree.base_node import SN_ScriptingBaseNode, SN_GenericPropertyGroup


class SN_OT_RandomIndex(bpy.types.Operator):
    bl_idname = "sn.random_index"
    bl_label = "New Random"
    bl_description = "Shows you a new random item"
    bl_options = {"REGISTER","UNDO","INTERNAL"}

    max_value: bpy.props.IntProperty()
    node: bpy.props.StringProperty()

    def execute(self, context):
        node = context.space_data.node_tree.nodes[self.node]
        node.index = randint(0,self.max_value)
        return {"FINISHED"}



class SN_LoFiNode(bpy.types.Node, SN_ScriptingBaseNode):

    bl_idname = "SN_LoFiNode"
    bl_label = "LoFi"
    # bl_icon = "GRAPH"
    bl_width_default = 200

    node_options = {
        "default_color": (0.2,0.2,0.2)
    }
    
    links = [
        ("Potsu Mix", "https://www.youtube.com/watch?v=FSnuF1FPSIU&list=PLp7HpIyLajPJM1np34q3Sad8DjDq2gkJd&ab_channel=potsu-Topic"),
        ("Relax/Study", "https://www.youtube.com/watch?v=5qap5aO4i9A&ab_channel=ChilledCow"),
        ("Sleep/Chill", "https://www.youtube.com/watch?v=DWcJFNfaw9c&ab_channel=ChilledCow"),
        ("Chillhop Radio", "https://www.youtube.com/watch?v=5yx6BWlEVcY&ab_channel=ChillhopMusic"),
        ("LoFi HipHop", "https://www.youtube.com/watch?v=0te6noMKffA&ab_channel=Netizens"),
        ("StarWars LoFi", "https://www.youtube.com/watch?v=78cyA-aGaKc&t=108s&ab_channel=Amemos-Ambience"),
        ("Samurai", "https://www.youtube.com/watch?v=jrTMMG0zJyI&t=9s&ab_channel=thebootlegboy"),
        ("Code-Fi", "https://www.youtube.com/watch?v=f02mOEt11OQ&ab_channel=TheAMPChannel"),
        ("LoFi Jazz", "https://www.youtube.com/watch?v=esX7SFtEjHg&ab_channel=CodePioneers"),
        ("Minecraft LoFi", "https://www.youtube.com/watch?v=hy0bAbznU6g&ab_channel=SolivagantSounds"),
        ("Late Night Nostalgia", "https://www.youtube.com/watch?v=dLmyp3xMsAo&ab_channel=DreamhopMusic"),
        ("Coffee Shop Radio", "https://www.youtube.com/watch?v=-5KAN9_CzSA&ab_channel=STEEZYASFUCK"),
        ("Old Songs LoFi", "https://www.youtube.com/watch?v=bPPiuludHKg&ab_channel=Lo-fiMusic"),
        ("Mind On Clouds", "https://www.youtube.com/watch?v=Hdncb04CdWw&ab_channel=TunableMusic"),
        ("Chill Beats", "https://www.youtube.com/watch?v=rA56B4JyTgI&ab_channel=WillSmith"),
        ("ibr Beats", "https://soundcloud.com/i-b-r/popular-tracks")
        ]
    
    index: bpy.props.IntProperty(default=0)
    
    def on_create(self,context):
        self.index = randint(0,len(self.links)-1)

    def on_copy(self,node):
        self.index = randint(0,len(self.links)-1)

    def draw_node(self,context,layout):
        box = layout.box()
        col = box.column()
        col.label(text="This node is for your enjoyment!",icon="FUND")
        col.label(text="Have a really nice day!",icon="BLANK1")

        row = layout.row(align=True)
        row.scale_y = 1.5
        row.operator("wm.url_open",text=self.links[self.index][0],depress=True,icon="FILE_SOUND").url = self.links[self.index][1]
        op = row.operator("sn.random_index",text="",icon="FILE_REFRESH",depress=True)
        op.node = self.name
        op.max_value = len(self.links)-1