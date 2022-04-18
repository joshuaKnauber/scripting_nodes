import bpy
import json


class SN_OT_CopyCommand(bpy.types.Operator):
    bl_idname = "sn.copy_command"
    bl_label = "Copy Command"
    bl_description = "Copies the command to post in the discord server"
    bl_options = {"REGISTER","UNDO","INTERNAL"}

    url: bpy.props.StringProperty(default="",options={"SKIP_SAVE"})
    price: bpy.props.StringProperty(default="Free",options={"SKIP_SAVE"})
    blender: bpy.props.BoolProperty(default=False,options={"SKIP_SAVE"})

    def execute(self, context):
        sn = bpy.context.scene.sn
            
        addon_info = {
            "name": sn.addon_name,
            "description": sn.description,
            "category": sn.category if not sn.category == 'CUSTOM' else sn.custom_category,
            "author": sn.author,
            "blender_version": list(tuple(sn.blender)),
            "addon_version": list(tuple(sn.version)),
            "external": self.url != "",
            "url": self.url,
            "price": self.price,
            "blend": self.blender,
            "blend_url": "",
            "user": 0,
            "serpens_version": 3
        }

        if self.url == "":
            addon_info["url"] = ""
            addon_info["price"] = ""

        bpy.context.window_manager.clipboard = json.dumps(addon_info)

        self.report({"INFO"},message="Copied successfully!")
        return {"FINISHED"}


class SN_OT_ExportToMarketplaceAddon(bpy.types.Operator):
    bl_idname = "sn.export_to_marketplace"
    bl_label = "Export Addon To Marketplace"
    bl_description = "Exports the active node tree to the marketplace"
    bl_options = {"REGISTER","UNDO","INTERNAL"}

    url: bpy.props.StringProperty(default="",name="Addon URL",description="Enter the url to your addon here")
    price: bpy.props.StringProperty(default="Free",name="Addon Price",description="Enter the price of your addon here")
    blender: bpy.props.BoolProperty(default=False,options={"SKIP_SAVE"})

    upload_type: bpy.props.EnumProperty(name="Upload Type",items=[("DIRECT","Direct Upload","Upload the addon directly"),("URL","External Link","Provide an external url for your addon")])

    expand_1: bpy.props.BoolProperty(default=True,name="Expand")
    expand_2: bpy.props.BoolProperty(default=False,name="Expand")
    expand_3: bpy.props.BoolProperty(default=False,name="Expand")

    @classmethod
    def poll(cls, context):
        return True

    def execute(self, context):
        return {"FINISHED"}

    def draw(self,context):
        box = self.layout.box()
        box.label(text="If you think your addon is interesting to others you can share it!",icon="FUND")

        self.layout.separator()

        self.layout.prop(self,"upload_type",expand=True,text=" ")

        self.layout.separator()

        box = self.layout.box()
        box.prop(self,"expand_1",text="Step 1",emboss=False,toggle=True,icon="DISCLOSURE_TRI_DOWN" if self.expand_1 else "DISCLOSURE_TRI_RIGHT")
        if self.expand_1:
            col = box.column(align=True)
            col.label(text="    • Set your addons name, description, version, ...")
            col.label(text="    • If you want to update an addon use the same name")
            col.label(text="    • Select if you want to upload your blend file with the node tree")
            col.separator()
            row = col.row(align=True)
            row.label(icon="BLANK1")
            row.prop(self,"blender", text="Upload blend file")
            row.label(icon="BLANK1")

        self.layout.separator()

        box = self.layout.box()
        box.prop(self,"expand_2",text="Step 2",emboss=False,toggle=True,icon="DISCLOSURE_TRI_DOWN" if self.expand_2 else "DISCLOSURE_TRI_RIGHT")
        if self.expand_2:
            col = box.column(align=False)

            if self.upload_type == "DIRECT":
                col.label(text="    • Go in the #marketplace channel on discord and post the following:")
                row = col.row(align=True)
                split = row.split(factor=0.03)
                split.label(text=" ")
                op = split.operator("sn.copy_command",text="Click To Copy!",icon="COPYDOWN")
                op.blender = self.blender
                row.operator("wm.url_open",text="",icon_value=bpy.context.scene.sn_icons[ "discord" ].icon_id).url = "https://discord.com/invite/NK6kyae"
                row.label(text=" ")
                col.separator()
                col.label(text="    • You will be asked to upload your addon. Export it and do so.")

            elif self.upload_type == "URL":
                row = col.row()
                row.label(text="    • Paste the link to your addon in here:")
                row.prop(self,"url", text="")
                col.separator()
                row = col.row()
                row.label(text="    • Enter the price of your addon here:")
                row.prop(self,"price", text="")

        if self.upload_type == "URL":
            self.layout.separator()

            box = self.layout.box()
            box.prop(self,"expand_3",text="Step 3",emboss=False,toggle=True,icon="DISCLOSURE_TRI_DOWN" if self.expand_3 else "DISCLOSURE_TRI_RIGHT")
            if self.expand_3:
                col = box.column(align=False)
                col.label(text="    • Go in the #marketplace channel on discord and post the following:")
                row = col.row(align=True)
                split = row.split(factor=0.03)
                split.label(text=" ")
                op = split.operator("sn.copy_command",text="Click To Copy!",icon="COPYDOWN")
                op.url = self.url
                op.price = self.price
                op.blender = self.blender
                row.operator("wm.url_open",text="",icon_value=bpy.context.scene.sn_icons[ "discord" ].icon_id).url = "https://discord.com/invite/NK6kyae"
                row.label(text=" ")


    def invoke(self, context, event):
        return context.window_manager.invoke_popup(self, width=500)